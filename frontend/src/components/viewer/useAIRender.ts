/**
 * useAIRender — React hook for the fal.ai FLUX image-to-image render pipeline.
 *
 * 4-face approach: rotates the camera to 4 bearings around the building,
 * captures each view, sends all 4 to fal.ai in parallel with the same seed,
 * and swaps the visible overlay based on the current map bearing.
 */
import { useState, useCallback, useRef } from 'react';
import { fal } from '@fal-ai/client';
import type { Map as MapboxMap } from 'mapbox-gl';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AIRenderStyle {
  id: string;
  label: string;
  prompt: string;
  /** Optional negative prompt fragments */
  negative?: string;
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
  /** Guidance scale — FLUX recommendation is 3.5 */
  guidanceScale?: number;
  /** Optional reference image URL or data-URI for IP-Adapter style transfer */
  referenceImageUrl?: string;
  /** IP-Adapter strength (0–1) */
  referenceStrength?: number;
  /** Archetype positive prompt — appended to the style prompt */
  archetypePrompt?: string;
  /** Archetype negative prompt — appended to the negative prompt */
  archetypeNegative?: string;
  /** Reference image URLs from archetype selections (first used for IP-Adapter) */
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
   * Should instruct the AI to replace the pink massing block with a
   * photorealistic building while keeping surrounding context intact.
   */
  mapOverlayPrompt?: string;
  /** Negative prompt from enriched archetype renderPrompt */
  mapOverlayNegative?: string;
}

export interface AIRenderResult {
  /** URL of the generated image (fal.ai CDN) */
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
  /** Generate a full-quality render with a locked seed. By default renders from current view only (single-view). */
  renderFull: (map: MapboxMap, options: AIRenderOptions, seed: number, singleView?: boolean) => Promise<AIRenderResult | null>;
  /** 4-face render results — one per bearing */
  faceRenders: FaceRender[];
  /** Whether a render is currently in flight */
  isRendering: boolean;
  /** 0–100 progress estimate */
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
// Style presets
// ---------------------------------------------------------------------------

export const AI_RENDER_STYLES: AIRenderStyle[] = [
  {
    id: 'modern-glass',
    label: 'Modern Glass',
    prompt:
      'aerial oblique photograph of a modern glass and steel mixed-use development, floor-to-ceiling glazing, reflective facades, rooftop terraces with greenery, high-end urban architecture, sunny day, sharp shadows, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, low quality, blurry, text, watermark',
  },
  {
    id: 'warm-brick',
    label: 'Warm Brick',
    prompt:
      'aerial oblique photograph of a contemporary brick and timber residential development, warm red brick facades, timber balconies, courtyard gardens, Scandinavian architecture style, golden hour light, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, low quality, blurry, text, watermark',
  },
  {
    id: 'campus-green',
    label: 'Green Campus',
    prompt:
      'aerial oblique photograph of a sustainable green campus development, extensive green roofs, solar panels, mature trees, bioswale landscaping, LEED-certified architecture, bright daylight, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, low quality, blurry, text, watermark',
  },
  {
    id: 'urban-mixed',
    label: 'Urban Mixed-Use',
    prompt:
      'aerial oblique photograph of a vibrant urban mixed-use district, retail podiums with residential towers above, active street frontage, outdoor dining areas, street trees, pedestrian plazas, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, low quality, blurry, text, watermark',
  },
  {
    id: 'waterfront',
    label: 'Waterfront',
    prompt:
      'aerial oblique photograph of a luxury waterfront development, marina promenade, curved glass facades reflecting water, boardwalk with restaurants, sailing boats, blue sky, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, low quality, blurry, text, watermark',
  },
  {
    id: 'heritage-modern',
    label: 'Heritage Modern',
    prompt:
      'aerial oblique photograph of a heritage-inspired modern development, stone and glass facades, arched windows, pitched roofs with contemporary dormers, cobblestone plaza, warm afternoon light, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, low quality, blurry, text, watermark',
  },
  {
    id: 'hyper-realistic',
    label: 'Hyper Realistic',
    prompt:
      'ultra-photorealistic DSLR photograph of a modern urban development, shallow depth of field, 85mm lens, tilt-shift bokeh, natural sunlight, crisp detail, architectural photography, commercial real-estate quality, 8k',
    negative: 'cartoon, illustration, sketch, painting, low quality, blurry, text, watermark, artistic, stylized',
  },
  {
    id: 'watercolour',
    label: 'Watercolour',
    prompt:
      'delicate watercolour illustration of an urban development, soft colour washes, visible paper texture, hand-painted architectural rendering, loose brushwork, muted earth tones, professional presentation board style',
    negative: 'photorealistic, photograph, 3D render, sharp edges, digital, neon, low quality, blurry',
  },
  {
    id: 'architectural-sketch',
    label: 'Arch Sketch',
    prompt:
      'architectural pencil sketch of an urban development, hand-drawn line work, cross-hatching shading, fine detail, vellum paper, professional design sketch, entourage figures, ink and graphite, presentation quality',
    negative: 'photorealistic, photograph, colour, painting, 3D render, low quality, blurry, text, watermark',
  },
  {
    id: 'cinematic-dusk',
    label: 'Cinematic Dusk',
    prompt:
      'cinematic golden hour photograph of an urban development, dramatic warm lighting, long amber shadows, glowing interior lights, reflective wet pavement, volumetric atmosphere, film grain, anamorphic lens flare, 8k',
    negative: 'cartoon, illustration, sketch, midday, flat lighting, low quality, blurry, text, watermark',
  },
  {
    id: 'photomontage',
    label: 'Photomontage',
    prompt:
      'professional architectural photomontage of a development inserted into real urban context, composite photography, matched lighting and perspective, surrounding neighbourhood visible, planning application quality, photorealistic, 8k',
    negative: 'cartoon, illustration, sketch, painting, floating, disconnected, low quality, blurry, text, watermark',
  },
  {
    id: 'planning-diagram',
    label: 'Planning Diagram',
    prompt:
      'clean urban planning diagram of a development site, flat colours, labelled zones, axonometric projection, massing study, colour-coded land use, minimal shadow, professional planning document, vector-style clarity',
    negative: 'photorealistic, photograph, painterly, sketch, low quality, blurry, noisy, text overlay, watermark',
  },
];

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Nano Banana 2 Edit — Google's Gemini-based image editor that semantically
 *  understands what to change vs. preserve. No mask needed — the model reasons
 *  about which regions to transform based on the prompt. */
const FAL_MODEL_ID = 'fal-ai/nano-banana-2/edit';
/** Legacy FLUX model ID — kept for reference / fallback */
const _LEGACY_FLUX_MODEL_ID = 'fal-ai/flux/dev/image-to-image';
void _LEGACY_FLUX_MODEL_ID;

const DEFAULT_STRENGTH = 0.58;
const DEFAULT_STEPS = 28;    // Used by legacy FLUX model
const DEFAULT_GUIDANCE = 3.5; // Used by legacy FLUX model
void DEFAULT_STEPS; void DEFAULT_GUIDANCE; // suppress unused warnings — kept for FLUX fallback
const DEFAULT_STYLE = 'modern-glass';

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

/** Read the fal.ai API key from Vite env */
function getFalKey(): string {
  return import.meta.env.VITE_FAL_KEY || '';
}

/** Compute the geographic bounding box of a polygon [[lng,lat],...] with padding factor */
function zoneBounds(coords: number[][], padding = 0.3): { west: number; south: number; east: number; north: number } {
  let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity;
  for (const [lng, lat] of coords) {
    if (lng < west) west = lng;
    if (lng > east) east = lng;
    if (lat < south) south = lat;
    if (lat > north) north = lat;
  }
  // Add padding so the building isn't right at the edges
  const lngPad = (east - west) * padding;
  const latPad = (north - south) * padding;
  return {
    west: west - lngPad,
    south: south - latPad,
    east: east + lngPad,
    north: north + latPad,
  };
}

/** Capture the Mapbox canvas as a PNG Blob */
function captureMapCanvasBlob(map: MapboxMap): Promise<Blob> {
  const canvas = map.getCanvas();
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error('Failed to capture map canvas as blob'));
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
      // Small extra delay to ensure tiles are rendered
      setTimeout(resolve, 300);
    };
    map.on('idle', onIdle);
  });
}

/** Build the full prompt from style + archetype + custom additions */
function buildPrompt(options: AIRenderOptions): string {
  // If we have a specific map-overlay prompt from the enriched archetype, use it directly
  if (options.mapOverlayPrompt?.trim()) {
    let prompt = options.mapOverlayPrompt.trim();
    if (options.customPrompt?.trim()) {
      prompt += ', ' + options.customPrompt.trim();
    }
    return prompt;
  }

  // Fallback to generic style preset
  const styleId = options.renderStyleId || options.style || DEFAULT_STYLE;
  const preset = AI_RENDER_STYLES.find((s) => s.id === styleId) || AI_RENDER_STYLES[0];
  let prompt = preset.prompt;
  if (options.archetypePrompt?.trim()) {
    prompt += ', ' + options.archetypePrompt.trim();
  }
  if (options.customPrompt?.trim()) {
    prompt += ', ' + options.customPrompt.trim();
  }
  return prompt;
}

/** Build the negative prompt (reserved for future use with models that support it) */
function _buildNegative(options: AIRenderOptions): string {
  // Use map-overlay negative prompt if available
  if (options.mapOverlayNegative?.trim()) {
    return options.mapOverlayNegative.trim() + ', changing background, modifying surroundings, altering satellite imagery outside the development area';
  }
  const styleId = options.renderStyleId || options.style || DEFAULT_STYLE;
  const preset = AI_RENDER_STYLES.find((s) => s.id === styleId) || AI_RENDER_STYLES[0];
  let negative = preset.negative || 'cartoon, illustration, sketch, low quality, blurry, text, watermark';
  if (options.archetypeNegative?.trim()) {
    negative += ', ' + options.archetypeNegative.trim();
  }
  negative += ', changing background, modifying surroundings, altering satellite imagery outside the development area';
  return negative;
}
void _buildNegative; // suppress unused warning

/** Determine which face should be visible based on current map bearing */
function getActiveFaceLabel(bearing: number): 'front' | 'right' | 'rear' | 'left' {
  // Normalize bearing to 0-360
  const b = ((bearing % 360) + 360) % 360;
  if (b >= 315 || b < 45) return 'front';
  if (b >= 45 && b < 135) return 'right';
  if (b >= 135 && b < 225) return 'rear';
  return 'left';
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

  // ── Single-face render (used for previews and internal calls) ──────

  const renderSingleFace = useCallback(
    async (
      screenshotUrl: string,
      bounds: [[number, number], [number, number], [number, number], [number, number]],
      options: AIRenderOptions,
      seed: number,
    ): Promise<AIRenderResult | null> => {
      const prompt = buildPrompt(options);

      // Build the edit prompt — Nano Banana 2 Edit semantically understands
      // what to change vs. preserve, so we describe the edit explicitly.
      // The prompt describes replacing flat colored overlay shapes with realistic development.
      const editInstruction = options.mapOverlayPrompt
        ? `This is a satellite/aerial photo of a real neighbourhood with colored overlay shapes drawn on top marking development zones. Replace the colored overlay shapes with ${prompt}. The colored shapes should become photorealistic buildings, houses, parks, and streets as seen from above in satellite imagery. Keep everything outside the colored shapes exactly the same — preserve all existing roads, houses, trees, and terrain. The result should look like a real Google Earth satellite photo of a completed development.`
        : `This is a satellite/aerial photo of a real neighbourhood with colored overlay shapes drawn on top marking development zones. Replace every colored overlay shape with photorealistic development matching its color: yellow shapes become residential houses with rooftops and gardens, red/orange shapes become commercial buildings with flat roofs and parking, purple shapes become mixed-use mid-rise buildings, green shapes become landscaped parks with trees and paths, blue shapes become institutional buildings. ${prompt}. Keep everything outside the colored shapes exactly the same — preserve all existing roads, houses, trees, and terrain. The result should look like a real Google Earth satellite photo of a completed development.`;

      // Collect reference images: screenshot + any archetype reference images
      const imageUrls = [screenshotUrl];
      if (options.referenceImageUrls?.length) {
        // Add archetype reference images (Nano Banana 2 supports up to 14)
        for (const refUrl of options.referenceImageUrls.slice(0, 4)) {
          imageUrls.push(refUrl);
        }
      } else if (options.referenceImageUrl) {
        imageUrls.push(options.referenceImageUrl);
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const body: Record<string, any> = {
        prompt: editInstruction,
        image_urls: imageUrls,
        resolution: '2K',
        aspect_ratio: 'auto',
        seed,
        output_format: 'png',
        safety_tolerance: '6',
        num_images: 1,
        thinking_level: 'high',
      };

      console.log('[AIRender] Nano Banana 2 Edit request:', {
        model: FAL_MODEL_ID,
        prompt: editInstruction.slice(0, 200) + '...',
        imageCount: imageUrls.length,
        imageUrls: imageUrls.map(u => u.slice(0, 80) + '...'),
        seed,
      });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let data: any;
      try {
        data = await fal.subscribe(FAL_MODEL_ID, {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          input: body as any,
          logs: true,
          onQueueUpdate: (update) => {
            console.log('[AIRender] Queue update:', update.status);
          },
        });
      } catch (falErr) {
        console.error('[AIRender] fal.ai API error:', falErr);
        throw falErr;
      }

      console.log('[AIRender] Raw response keys:', Object.keys(data ?? {}));
      console.log('[AIRender] Raw response data keys:', Object.keys(data?.data ?? {}));

      const images = data?.data?.images ?? data?.images;
      if (!images || !Array.isArray(images) || images.length === 0) {
        console.error('[AIRender] No images in response. Full response:', JSON.stringify(data).slice(0, 500));
        return null;
      }
      const imageUrl = images[0]?.url;
      if (!imageUrl) {
        console.error('[AIRender] Image object has no url:', images[0]);
        return null;
      }

      return {
        imageUrl,
        bounds,
        seed: data?.data?.seed ?? data?.seed ?? seed,
        prompt,
      };
    },
    [],
  );

  // ── Single render (current camera position) ────────────────────────

  const render = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult | null> => {
      const falKey = getFalKey();
      if (!falKey) {
        setError('VITE_FAL_KEY is not set. Add it to your .env file.');
        return null;
      }

      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsRendering(true);
      setProgress(5);
      setError(null);
      setStatusMessage('Capturing view...');

      try {
        fal.config({ credentials: falKey });
        const blob = await captureMapCanvasBlob(map);
        const file = new File([blob], 'map-capture.png', { type: 'image/png' });
        const screenshotUrl = await fal.storage.upload(file);
        const bounds = getMapBounds(map);
        setProgress(20);
        setStatusMessage('Rendering...');

        const seed = options.seed ?? Math.floor(Math.random() * 2147483647);
        const result = await renderSingleFace(screenshotUrl, bounds, options, seed);

        if (!result) throw new Error('fal.ai returned no images');

        setResult(result);
        setProgress(100);
        setStatusMessage('Complete');
        setIsRendering(false);
        return result;
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
    [renderSingleFace],
  );

  // ── Zone-targeted render ──────────────────────────────────────────

  const renderZone = useCallback(
    async (
      map: MapboxMap,
      zoneCoords: number[][],
      options: AIRenderOptions = {},
    ): Promise<AIRenderResult | null> => {
      const falKey = getFalKey();
      if (!falKey) {
        setError('VITE_FAL_KEY is not set. Add it to your .env file.');
        return null;
      }

      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsRendering(true);
      setProgress(5);
      setError(null);
      setStatusMessage('Zooming to building zone...');

      try {
        fal.config({ credentials: falKey });

        // Save bearing for consistent framing
        const originalBearing = map.getBearing();

        // Compute zone bounding box and zoom the camera to frame it
        const zb = zoneBounds(zoneCoords, 0.5);

        // Fly the camera to frame the zone at 45° pitch
        map.fitBounds(
          [[zb.west, zb.south], [zb.east, zb.north]],
          { padding: 60, pitch: 45, bearing: originalBearing, duration: 0 },
        );

        // Wait for map to settle
        await new Promise<void>((resolve) => {
          const onIdle = () => { map.off('idle', onIdle); setTimeout(resolve, 500); };
          map.on('idle', onIdle);
        });

        setProgress(15);
        setStatusMessage('Capturing zone view...');

        const blob = await captureMapCanvasBlob(map);
        const file = new File([blob], 'zone-capture.png', { type: 'image/png' });
        const screenshotUrl = await fal.storage.upload(file);

        // Use the current (zoomed) viewport bounds for the overlay
        const bounds = getMapBounds(map);

        setProgress(30);
        setStatusMessage('Rendering building facade...');

        const seed = options.seed ?? Math.floor(Math.random() * 2147483647);

        // Log what we're sending
        const prompt = buildPrompt(options);
        console.log('[AIRender] Zone render prompt:', prompt);
        console.log('[AIRender] Using mapOverlayPrompt:', !!options.mapOverlayPrompt);
        console.log('[AIRender] Strength:', options.controlStrength ?? DEFAULT_STRENGTH);

        const result = await renderSingleFace(screenshotUrl, bounds, options, seed);

        if (!result) throw new Error('fal.ai returned no images');

        // Stay zoomed in so the user can see the rendered building
        // (camera was already positioned by fitBounds above)

        setResult(result);
        setProgress(100);
        setStatusMessage('Complete — building rendered');
        setIsRendering(false);
        return result;
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
    [renderSingleFace],
  );

  // ── Preview renders (3 in parallel, single face each) ──────────────

  const renderPreviews = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult[]> => {
      const falKey = getFalKey();
      if (!falKey) {
        setError('VITE_FAL_KEY is not set. Add it to your .env file.');
        return [];
      }

      setIsRendering(true);
      setProgress(5);
      setError(null);
      setPreviews([]);
      setSelectedPreviewIndex(null);
      setResult(null);
      setStatusMessage('Capturing view...');

      try {
        fal.config({ credentials: falKey });
        const blob = await captureMapCanvasBlob(map);
        const file = new File([blob], 'map-capture.png', { type: 'image/png' });
        const screenshotUrl = await fal.storage.upload(file);
        const bounds = getMapBounds(map);
        setProgress(15);
        setStatusMessage('Generating 3 previews...');

        const seeds = Array.from({ length: 3 }, () => Math.floor(Math.random() * 2147483647));

        const promises = seeds.map((seed) =>
          renderSingleFace(screenshotUrl, bounds, options, seed),
        );

        const results = await Promise.all(promises);
        const successful = results.filter((r): r is AIRenderResult => r !== null);

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
    [renderSingleFace],
  );

  // ── 4-face full render ─────────────────────────────────────────────

  const renderFull = useCallback(
    async (
      map: MapboxMap,
      options: AIRenderOptions,
      seed: number,
      singleView = true,
    ): Promise<AIRenderResult | null> => {
      const falKey = getFalKey();
      if (!falKey) {
        setError('VITE_FAL_KEY is not set. Add it to your .env file.');
        return null;
      }

      setIsRendering(true);
      setProgress(5);
      setError(null);
      setFaceRenders([]);

      try {
        fal.config({ credentials: falKey });

        // ── Single-view mode: render from user's current perspective ──
        if (singleView) {
          setStatusMessage('Capturing current view...');
          const blob = await captureMapCanvasBlob(map);
          const file = new File([blob], 'full-render-capture.png', { type: 'image/png' });
          const screenshotUrl = await fal.storage.upload(file);
          const bounds = getMapBounds(map);
          setProgress(25);
          setStatusMessage('Rendering full quality...');

          const fullResult = await renderSingleFace(screenshotUrl, bounds, options, seed);
          if (!fullResult) throw new Error('fal.ai returned no images');

          setResult(fullResult);
          setProgress(100);
          setStatusMessage('Complete — full quality render');
          setIsRendering(false);
          return fullResult;
        }

        // ── 4-face mode: rotate camera to 4 bearings ──
        setStatusMessage('Capturing 4 views...');

        // Save original camera state
        const originalBearing = map.getBearing();
        const originalPitch = map.getPitch();
        const originalCenter = map.getCenter();
        const originalZoom = map.getZoom();

        // Step 1: Capture 4 face screenshots
        const captures: { label: 'front' | 'right' | 'rear' | 'left'; url: string; bounds: [[number, number], [number, number], [number, number], [number, number]] }[] = [];

        for (let i = 0; i < FACE_BEARINGS.length; i++) {
          const face = FACE_BEARINGS[i];
          setStatusMessage(`Capturing ${face.label} view (${i + 1}/4)...`);
          setProgress(5 + i * 10);

          await easeMapTo(map, face.bearing, 45);

          const blob = await captureMapCanvasBlob(map);
          const file = new File([blob], `face-${face.label}.png`, { type: 'image/png' });
          const url = await fal.storage.upload(file);
          const bounds = getMapBounds(map);

          captures.push({ label: face.label, url, bounds });
        }

        // Restore original camera
        map.easeTo({
          bearing: originalBearing,
          pitch: originalPitch,
          center: originalCenter,
          zoom: originalZoom,
          duration: 500,
        });

        setProgress(45);
        setStatusMessage('Rendering all 4 faces...');

        // Step 2: Send all 4 to fal.ai in parallel with the same seed
        const renderPromises = captures.map((cap) =>
          renderSingleFace(cap.url, cap.bounds, options, seed)
            .then((result) => result ? { label: cap.label, bearing: FACE_BEARINGS.find(f => f.label === cap.label)!.bearing, result } as FaceRender : null)
            .catch(() => null),
        );

        const faceResults = await Promise.all(renderPromises);
        const successfulFaces = faceResults.filter((f): f is FaceRender => f !== null);

        setProgress(90);
        setStatusMessage('Applying textures...');

        setFaceRenders(successfulFaces);

        // Use the front face as the main result
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
    [renderSingleFace],
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

      // Add sources and layers for each face
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

      // Set initial visibility
      updateVisibility();

      // Listen for bearing changes
      map.on('rotate', updateVisibility);

      // Cleanup function
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
