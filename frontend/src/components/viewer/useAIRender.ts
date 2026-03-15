/**
 * useAIRender — React hook for the fal.ai FLUX.1 Depth aerial render pipeline.
 *
 * Captures the current Mapbox GL canvas, sends it to fal.ai with a depth
 * ControlNet, and returns the photorealistic result image URL + geographic
 * bounds for overlay.
 */
import { useState, useCallback, useRef } from 'react';
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
  /** 0–1 — how closely the AI follows the massing geometry */
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
  imageSize?: { width: number; height: number };
  /** Render style id — alias for style, used by expanded catalog */
  renderStyleId?: string;
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

export interface UseAIRenderReturn {
  /** Trigger a render. Resolves with the result or null on failure. */
  render: (map: MapboxMap, options?: AIRenderOptions) => Promise<AIRenderResult | null>;
  /** Generate 3 preview renders in parallel with different seeds (768×768, 25 steps) */
  renderPreviews: (map: MapboxMap, options?: AIRenderOptions) => Promise<AIRenderResult[]>;
  /** Generate a full-quality render with a locked seed (1024×1024, 50 steps) */
  renderFull: (map: MapboxMap, options: AIRenderOptions, seed: number) => Promise<AIRenderResult | null>;
  /** Whether a render is currently in flight */
  isRendering: boolean;
  /** 0–100 progress estimate (fal.ai doesn't stream progress, so this is heuristic) */
  progress: number;
  /** Last successful result */
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

const FAL_ENDPOINT = 'https://fal.run/fal-ai/flux-general';
const DEFAULT_CONTROL_STRENGTH = 0.85;
const DEFAULT_STEPS = 28;
const DEFAULT_GUIDANCE = 3.5;
const DEFAULT_STYLE = 'modern-glass';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Read the fal.ai API key from Vite env */
function getFalKey(): string {
  return (
    (typeof import.meta !== 'undefined' && (import.meta as any)?.env?.VITE_FAL_KEY) || ''
  );
}

/** Capture the Mapbox canvas as a PNG data-URI */
function captureMapCanvas(map: MapboxMap): string {
  const canvas = map.getCanvas();
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
  // Mapbox image source expects: top-left, top-right, bottom-right, bottom-left
  return [nw, ne, se, sw];
}

/** Build the full prompt from style + archetype + custom additions */
function buildPrompt(options: AIRenderOptions): string {
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

/** Build the negative prompt */
function buildNegative(options: AIRenderOptions): string {
  const styleId = options.renderStyleId || options.style || DEFAULT_STYLE;
  const preset = AI_RENDER_STYLES.find((s) => s.id === styleId) || AI_RENDER_STYLES[0];
  let negative = preset.negative || 'cartoon, illustration, sketch, low quality, blurry, text, watermark';
  if (options.archetypeNegative?.trim()) {
    negative += ', ' + options.archetypeNegative.trim();
  }
  return negative;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAIRender(): UseAIRenderReturn {
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<AIRenderResult | null>(null);
  const [previews, setPreviews] = useState<AIRenderResult[]>([]);
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    setResult(null);
    setPreviews([]);
    setSelectedPreviewIndex(null);
    setError(null);
    setProgress(0);
  }, []);

  const render = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult | null> => {
      const falKey = getFalKey();
      if (!falKey) {
        const msg = 'VITE_FAL_KEY is not set. Add it to your .env file.';
        setError(msg);
        return null;
      }

      // Abort any in-flight request
      if (abortRef.current) {
        abortRef.current.abort();
      }
      const controller = new AbortController();
      abortRef.current = controller;

      setIsRendering(true);
      setProgress(5);
      setError(null);

      try {
        // 1. Capture the map canvas
        const screenshotDataUri = captureMapCanvas(map);
        const bounds = getMapBounds(map);
        setProgress(15);

        // 2. Build the prompt
        const prompt = buildPrompt(options);
        const negativePrompt = buildNegative(options);
        setProgress(20);

        // 3. Build the request body
        const controlStrength = options.controlStrength ?? DEFAULT_CONTROL_STRENGTH;
        const steps = options.steps ?? DEFAULT_STEPS;
        const guidance = options.guidanceScale ?? DEFAULT_GUIDANCE;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const body: Record<string, any> = {
          prompt,
          negative_prompt: negativePrompt,
          num_inference_steps: steps,
          guidance_scale: guidance,
          num_images: 1,
          enable_safety_checker: false,
          output_format: 'png',
          controlnets: [
            {
              path: 'depth',
              control_image_url: screenshotDataUri,
              conditioning_scale: controlStrength,
            },
          ],
        };

        // Explicit seed for reproducibility
        if (options.seed != null) {
          body.seed = options.seed;
        }

        // Override output dimensions
        if (options.imageSize) {
          body.image_size = options.imageSize;
        }

        // IP-Adapter reference image — explicit upload takes priority,
        // then falls back to first archetype reference URL
        const ipAdapterUrl =
          options.referenceImageUrl ||
          options.referenceImageUrls?.[0] ||
          undefined;

        if (ipAdapterUrl) {
          body.ip_adapter = [
            {
              ip_adapter_image_url: ipAdapterUrl,
              ip_adapter_scale: options.referenceStrength ?? 0.6,
            },
          ];
        }

        setProgress(25);

        // 4. Call fal.ai
        const response = await fetch(FAL_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Key ${falKey}`,
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        setProgress(70);

        if (!response.ok) {
          const text = await response.text().catch(() => '');
          throw new Error(`fal.ai returned ${response.status}: ${text.slice(0, 200)}`);
        }

        const data = await response.json();
        setProgress(90);

        // 5. Extract result
        const images = data?.images;
        if (!images || !Array.isArray(images) || images.length === 0) {
          throw new Error('fal.ai returned no images');
        }

        const imageUrl = images[0]?.url;
        if (!imageUrl) {
          throw new Error('fal.ai returned an image entry with no URL');
        }

        const renderResult: AIRenderResult = {
          imageUrl,
          bounds,
          seed: data.seed,
          prompt,
        };

        setResult(renderResult);
        setProgress(100);
        setIsRendering(false);
        return renderResult;
      } catch (err: unknown) {
        if ((err as Error)?.name === 'AbortError') {
          // Cancelled — don't set error
          setIsRendering(false);
          setProgress(0);
          return null;
        }
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        return null;
      }
    },
    [],
  );

  // ── Preview renders (3 in parallel, lower quality) ────────────────────

  const renderPreviews = useCallback(
    async (map: MapboxMap, options: AIRenderOptions = {}): Promise<AIRenderResult[]> => {
      setIsRendering(true);
      setProgress(5);
      setError(null);
      setPreviews([]);
      setSelectedPreviewIndex(null);
      setResult(null);

      try {
        // Generate 3 random seeds
        const seeds = Array.from({ length: 3 }, () => Math.floor(Math.random() * 2147483647));

        setProgress(10);

        // Fire 3 renders in parallel at preview quality
        const promises = seeds.map((seed) =>
          render(map, {
            ...options,
            seed,
            imageSize: { width: 768, height: 768 },
            steps: 25,
          }),
        );

        // Wait for all — filter out nulls
        const results = await Promise.all(promises);
        const successful = results.filter((r): r is AIRenderResult => r !== null);

        setPreviews(successful);
        setProgress(100);
        setIsRendering(false);
        return successful;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setIsRendering(false);
        setProgress(0);
        return [];
      }
    },
    [render],
  );

  // ── Full-quality render with locked seed ─────────────────────────────

  const renderFull = useCallback(
    async (
      map: MapboxMap,
      options: AIRenderOptions,
      seed: number,
    ): Promise<AIRenderResult | null> => {
      return render(map, {
        ...options,
        seed,
        imageSize: { width: 1024, height: 1024 },
        steps: 50,
      });
    },
    [render],
  );

  return {
    render,
    renderPreviews,
    renderFull,
    isRendering,
    progress,
    result,
    previews,
    selectedPreviewIndex,
    setSelectedPreviewIndex,
    error,
    reset,
  };
}
