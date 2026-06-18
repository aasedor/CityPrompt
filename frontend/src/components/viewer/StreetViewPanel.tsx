/**
 * StreetViewPanel — floating panel that appears when the street view pegman
 * is placed on the map. Shows compass direction, rotation controls, and a
 * generate button. Displays the rendered street view in a modal.
 */
import { useState, useCallback } from 'react';
import { Eye, ArrowLeft, ArrowRight, Loader2, X, Download, Save, Wand2 } from 'lucide-react';
import { useViewerStore } from '@/store';
import { useStreetViewRender, type StreetViewResult } from './useStreetViewRender';
import type { SavedRender, SiteZone } from '@/types';
import toast from 'react-hot-toast';
import { getRenderImageKey, saveRenderedImage } from '@/utils/renderPersistence';
import { resolveApiFileUrl } from '@/services/api';
import { RenderEditModal } from './RenderEditModal';

const COMPASS_LABELS: Record<number, string> = {
  0: 'N', 45: 'NE', 90: 'E', 135: 'SE',
  180: 'S', 225: 'SW', 270: 'W', 315: 'NW',
};

const STREET_VIEW_STYLES = [
  // ── Realistic — photo-style final-stage visualization ──
  {
    id: 'photorealistic',
    label: 'Photo',
    prompt: 'Hyper-photorealistic street-level architectural visualization. Camera positioned at exact human eye-level using a 35mm prime lens at f/8 aperture ensuring deep focus and edge-to-edge sharpness. Golden hour on a clear day with warm low-angle directional sunlight casting long crisp high-contrast shadows across the sidewalk. Subtle hyper-realistic environmental details: specular reflections of adjacent buildings visible in glass facades, slight atmospheric haze, photorealistic street trees. Rendered in the style of Unreal Engine 5 with path-traced global illumination, 8K resolution, architectural digest photography.',
  },
  {
    id: 'photomontage',
    label: 'Montage',
    prompt: 'Professional architectural photomontage at street level, indistinguishable from a real photograph taken by a surveyor documenting an existing building. Shot on a Canon EOS R5 with a 35mm prime lens at f/8, ISO 200, from a tripod at exactly 1.6 meters height. The proposed building appears as if it has existed on this site for 1-2 years -- subtle concrete dust at the base, minor rainwater staining below window reveals, fingerprints and smudges on ground-floor entrance glass, worn threshold stones at doorways. The building sits within completely real street context: existing pavement with authentic repair patches and gum stains, real street furniture, actual adjacent buildings with their genuine patina and signage. Reflections in the new building ground-floor glazing show the actual street scene opposite including existing buildings and parked vehicles. Shadows cast by the new building fall correctly onto the real pavement and neighbouring facades matching the sun position. Slight depth of field -- building in sharp focus, background softening naturally beyond 80 meters. Overcast-bright sky with soft diffused light eliminating harsh shadows, typical of UK planning verified view photography. Natural sensor noise at ISO 200, subtle lens barrel distortion at frame edges. This is a planning application verified view, not an architectural marketing image.',
  },
  {
    id: 'atmospheric',
    label: 'Atmospheric',
    prompt: 'Premium real-time path-traced street-level architectural render (D5/Lumion/Unreal Engine 5 quality). Camera at human eye height (1.6m), 35mm prime lens at f/5.6 with deep but natural focus — foreground architectural detail tack-sharp, a gentle depth-of-field falloff softening the distant streetscape. Warm late-afternoon golden-hour sun, soft directional key light casting long clean shadows across the sidewalk. Soft path-traced global illumination with realistic ambient occlusion in reveals, recesses, and under canopies, plus clean contact shadows where elements meet the ground. Physically-based materials respond accurately to the light: low-iron glass with true reflections and subtle refraction, brushed stainless steel, board-formed and precast concrete, natural stone, warm timber cladding. Lush naturally-scattered street trees and planting. Subtle atmospheric perspective and a faint volumetric haze give depth — distant buildings read slightly cooler and softer. Balanced high dynamic range with clean controlled exposure, gentle bloom on the brightest highlights only, a refined filmic colour grade, and crisp edge-to-edge clarity. Award-winning architectural-magazine quality — premium, polished, and photoreal, not theatrical. For all existing surrounding context, treat the captured scene as ground truth to be sharpened, not reimagined: resolve the existing buildings, street, and landscape into their true real-world appearance while preserving their actual massing, proportions, and materials. Do not beautify, restyle, idealize, or replace existing structures. Reserve the premium polish for the proposed building only.',
  },
  {
    id: 'winter',
    label: 'Winter',
    prompt: 'Photorealistic winter street-level architectural scene. Snow accumulation on all horizontal surfaces -- rooftops, ledges, window sills, and parapets show realistic drift patterns. Bare deciduous trees with visible branch architecture and zero foliage. Evergreen conifers with heavy snow-load clumps on branches. Frost visible on metal railings, glass surfaces, and exposed stone. Plowed street surfaces with salt-grit residue, thin slush patches, and tire tracks in compacted snow. Cobblestone crevices packed with white snow while dark wet stone crowns create high-contrast grid pattern. Snow piled in sculptural windrows at curb edges. Warm incandescent glow spilling from shop windows and entrance lobbies contrasting against the cool winter palette. Pale blue-grey overcast sky with soft diffuse winter daylight. Low sun angle casting long blue-tinted shadows. Exhaled breath vapor from any figures. Increased specular reflectivity on all horizontal surfaces by 20% to simulate melt and ice sheen. Snow-capped stone lintels and frosted wrought-iron fences on heritage buildings.',
  },
  // ── Concept — hand-drawn / painterly early-stage exploration ──
  {
    id: 'watercolour',
    label: 'Watercolour',
    prompt: 'A beautiful, evocative architectural watercolour painting on rough cold-pressed watercolour paper. The artistic style is intentionally loose, expressive, and highly atmospheric, heavily utilizing traditional wet-on-wet painting techniques with visible fluid brushstrokes and natural unpredictable pigment bleeds at the edges of forms. Architecture outlined very loosely with delicate jittery black ink pen linework mimicking a masterful ink and wash architectural sketch. Colour palette of highly translucent luminous pastels — soft ochre and raw sienna for stone and facades, muted atmospheric cyan for sky, sap green and viridian for foliage, concentrated splashes of colour on awnings and signage to draw the eye. Lighting is bright and ethereal, leaving generous amounts of stark white negative space on the textured paper to represent glaring sunlight — the paper itself creates the highlights since watercolourists cannot paint white. Pigment granulation visible in shadow areas. Foreground facades rendered with tighter detail, background elements dissolve into soft suggestive washes. Masterful traditional media, concept art, architectural sketch.',
  },
  {
    id: 'charcoal',
    label: 'Charcoal',
    prompt: 'A highly detailed expressive architectural hand-sketch rendered in charcoal and graphite pencil on heavy textured cream sketching paper. The drawing style features loose kinetic gestural linework that accurately captures the perspective and vanishing points of the street. Full tonal range from deep compressed charcoal blacks in shadow areas to soft smudged mid-tones to bright paper whites on sunlit surfaces. Shading achieved through meticulous architectural crosshatching and subtle graphite smudging establishing volume and depth of recessed windows, doorways, and building facades. The image is strictly monochromatic with zero colour applied. The edges of the streetscape fade out loosely into the white of the paper giving it an authentic unfinished rapid-ideation sketchbook aesthetic. Foreground architecture sharp and detailed, background dissolves into atmospheric smudged tones. Visible charcoal texture and paper grain throughout. Precise architectural illustration, master draftsman techniques.',
  },
  {
    id: 'marker-render',
    label: 'Marker',
    prompt: 'A classic handcrafted architectural marker rendering on smooth bleedproof presentation paper. The scene is drafted with precise straight black ink linework using a technical pen defining all architectural edges and material boundaries. Colour and shading applied using simulated alcohol-based Copic design markers. The image must clearly display characteristic overlapping streaky marker strokes with visible stroke direction following surface planes, and subtle ink bleeds at the edges of colour blocks. Colour palette is vibrant but highly controlled — warm greys and ochres for building facades, olive and sap greens for landscape, bold teal and cerulean for sky. Stark white gaps deliberately left between marker strokes to represent highlights and reflected light. Bright optimistic illustrative lighting. White gel pen highlights on glass reflections and material edges. Entourage elements like trees and street furniture rendered in quick confident marker strokes. Traditional architectural presentation board aesthetic, retro design illustration, highly tactile.',
  },
  {
    id: 'pen-and-ink',
    label: 'Pen & Ink',
    prompt: 'A detailed architectural pen-and-ink line drawing of the streetscape on cream drawing paper. Strict ink-only linework with absolutely zero colour and zero tonal smudging — every mark is a deliberate line drawn by a technical pen. Strong perspective with vanishing points and accurate eye-level composition. Building facades defined by precise technical-pen linework with cross-hatching for shadow areas — denser hatching in deeper shadows, sparser hatching in mid-tones, cream paper showing through for highlights. Line-weight variation: delicate hairlines for distant elements, confident heavier lines for foreground edges. Stippling for foliage, paving texture, and weathered surfaces. Street furniture and entourage drawn with quick economical line work. Background facades dissolve into lighter sketchy linework. Cream paper glowing through as the brightest tones. Urban-sketcher tradition, masterful technical pen drawing, architectural illustration.',
  },
  // ── Stylized — bold, graphic, distinctive ──
  // (Plan group omitted — street view excludes orthographic styles by design.)
  {
    id: 'clay-model',
    label: 'Clay',
    prompt: 'A pristine physical white clay architectural massing model of the entire streetscape. The entirety of the scene — buildings, streets, sidewalks, trees, street furniture — is constructed from a single matte untextured white plaster material. There are absolutely zero colours or distinct material finishes present anywhere. All visual definition relies exclusively on high-quality Ambient Occlusion rendering to define sharp edges, depth, and spatial relationships of intersecting geometric volumes. Lighting is soft highly diffused studio softbox setup casting smooth gradient shadows across the pure white forms, emphasizing architectural massing and volumetric proportions without visual distractions. Trees represented as simplified smooth white sculptural forms. The scene resembles a physical foam-board scale model photographed in a professional studio. Minimalist clean exhibition-quality physical scale model, architectural review presentation.',
  },
  {
    id: 'collage',
    label: 'Collage',
    prompt: 'A vibrant post-digital architectural collage depicting the streetscape as a highly stylized mixed media composition resembling a physical mood board. Architecture represented by flat unshaded blocks of pastel colours and oversized mismatched photographic textures of brick concrete and wood applied like rough paper cut-outs with visible torn edges. Trees and landscape elements are vintage botanical illustration cut-outs pasted at varied scales. The sky is an abstract geometric pattern rather than realistic. Pedestrian figures represented by monochromatic vintage photographic cut-outs with stark white paper borders pasted seemingly at varied scales into the scene. Lighting is intentionally flat and illustrative emphasizing the overlapping layers and surreal disjointed scale of different elements. Visible paper texture and adhesive marks throughout. Avant-garde architectural visualization, artistic narrative presentation, Dadaist pop-art influences, design competition aesthetic.',
  },
  {
    id: 'pixel-art',
    label: 'Pixel Art',
    prompt: '16-bit pixel art architectural streetscape, strictly grid-aligned with every element constructed from uniform square pixels on a rigid pixel grid. Nearest-neighbour scaling with absolutely zero anti-aliasing, zero smoothing, zero sub-pixel rendering -- only hard stepped pixel edges throughout. Strict limited palette of exactly 16 carefully chosen colours. All shading and tonal transitions achieved exclusively through deliberate checkerboard dithering patterns and ordered Bayer-matrix dithering -- zero smooth gradients anywhere. Each window is an exact small pixel rectangle, each brick course a precise alternating pixel row, each roofline a clean 2:1 stepped pixel diagonal. Dark selective outlines on architectural edges transitioning to lighter colour outlines on sunlit sides. Warm amber pixel-glow from windows contrasting against cool blue-purple evening sky. Atmospheric pixel haze in the background with reduced palette depth for distance. Trees as stylized rounded pixel clusters with dithered foliage. SNES Final Fantasy VI town background, Chrono Trigger overworld, classic 16-bit JRPG city scene, demoscene pixel art, waneella atmospheric pixel cityscape.',
  },
] as const;

// UI grouping for the style picker — Plan group omitted because street view
// excludes orthographic styles by design.
const STREET_VIEW_STYLE_GROUPS = [
  { label: 'Realistic', ids: ['photorealistic', 'photomontage', 'atmospheric', 'winter'] },
  { label: 'Concept', ids: ['watercolour', 'charcoal', 'marker-render', 'pen-and-ink'] },
  { label: 'Stylized', ids: ['clay-model', 'collage', 'pixel-art'] },
] as const;

const STREET_VIEW_RENDER_MODELS = [
  { model: 'gemini-3.1-flash-image-preview', label: 'Gemini 3.1 Flash' },
  { model: 'gpt-image-2', label: 'GPT Image 2', imageQuality: 'auto' as const },
];
const STREET_VIEW_RENDER_LABEL = 'Gemini + GPT Image 2';

function escapeSvgText(value: string): string {
  return value.replace(/[<>&"]/g, (char) => ({
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
  }[char] || char));
}

function createErrorPreviewImage(providerLabel: string, message: string): string {
  const safeLabel = escapeSvgText(providerLabel);
  const safeMessage = escapeSvgText(message).slice(0, 320);
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
      <rect width="1200" height="675" fill="#1f2937"/>
      <rect x="44" y="44" width="1112" height="587" rx="18" fill="#111827" stroke="#ef4444" stroke-width="4"/>
      <text x="84" y="150" fill="#fca5a5" font-family="Arial, sans-serif" font-size="46" font-weight="700">${safeLabel}</text>
      <text x="84" y="216" fill="#ffffff" font-family="Arial, sans-serif" font-size="34" font-weight="700">Street view render failed</text>
      <foreignObject x="84" y="270" width="1032" height="260">
        <div xmlns="http://www.w3.org/1999/xhtml" style="color:#d1d5db;font-family:Arial,sans-serif;font-size:26px;line-height:1.35;word-break:break-word;">${safeMessage}</div>
      </foreignObject>
    </svg>
  `;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function compassLabel(angle: number): string {
  const norm = ((angle % 360) + 360) % 360;
  return COMPASS_LABELS[norm] || `${norm}°`;
}

interface StreetViewPanelProps {
  siteZones: SiteZone[];
  projectId?: string;
  /** When provided, captures 3D tiles from street level instead of clay render */
  globeCapture?: () => Promise<string | null>;
  onRenderSaved?: (render: SavedRender) => void;
}

export function StreetViewPanel({ siteZones, projectId, globeCapture, onRenderSaved }: StreetViewPanelProps) {
  const { streetViewPegman, setStreetViewAngle, setStreetViewPosition, setStreetViewActive } = useViewerStore();
  const { generateStreetView } = useStreetViewRender();
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<StreetViewResult | null>(null);
  const [previews, setPreviews] = useState<StreetViewResult[]>([]);
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedImageKeys, setSavedImageKeys] = useState<Set<string>>(() => new Set());
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');
  const [lightboxOpen, setLightboxOpen] = useState(false);
  // Real Street View / Places / satellite grounding, anchored at the pegman.
  // On by default (it helps); toggle off to A/B against a context-free render.
  const [useRealContext, setUseRealContext] = useState(true);
  const [includePeople, setIncludePeople] = useState(false);
  const [includeVehicles, setIncludeVehicles] = useState(false);
  const [editTarget, setEditTarget] = useState<SavedRender | null>(null);

  const toEditableStreetViewRender = useCallback((render: StreetViewResult): SavedRender => ({
    id: `street-view-${getRenderImageKey(render)}`,
    image_url: render.imageUrl,
    prompt: render.prompt || 'Street view render',
    style: render.providerLabel ? `street-view / ${render.providerLabel}` : 'street-view',
    model: render.model,
    image_quality: render.imageQuality,
    created_at: new Date().toISOString(),
  }), []);

  const saveStreetViewRender = useCallback(async (render: StreetViewResult, showToast = false) => {
    if (!projectId || render.error || !render.imageUrl) return null;

    const key = getRenderImageKey(render);
    if (savedImageKeys.has(key)) {
      if (showToast) toast.success('Already saved');
      return null;
    }

    const saved = await saveRenderedImage(
      projectId,
      render,
      render.providerLabel ? `street-view / ${render.providerLabel}` : 'street-view',
    );
    setSavedImageKeys((prev) => new Set(prev).add(key));
    onRenderSaved?.(saved);
    if (showToast) toast.success('Street view saved');
    return saved;
  }, [onRenderSaved, projectId, savedImageKeys]);

  const handleRotateLeft = useCallback(() => {
    if (!streetViewPegman) return;
    setStreetViewAngle(((streetViewPegman.angle - 45) + 360) % 360);
  }, [streetViewPegman, setStreetViewAngle]);

  const handleRotateRight = useCallback(() => {
    if (!streetViewPegman) return;
    setStreetViewAngle((streetViewPegman.angle + 45) % 360);
  }, [streetViewPegman, setStreetViewAngle]);

  const handleGenerate = useCallback(async () => {
    if (!streetViewPegman?.position) return;
    const pegmanPosition = streetViewPegman.position;
    const pegmanAngle = streetViewPegman.angle;
    setIsGenerating(true);
    try {
      // For re-renders: extract previous render base64 for dual anchoring
      let previousRenderBase64: string | undefined;
      if (result?.imageUrl?.startsWith('data:image/')) {
        previousRenderBase64 = result.imageUrl.split(',')[1];
      }
      setPreviews([]);
      setSelectedPreviewIndex(null);

      const styleObj = STREET_VIEW_STYLES.find(s => s.id === selectedStyle);
      const PHOTO_VARIANT_STYLES = ['photorealistic', 'photomontage', 'atmospheric', 'winter'];
      const styleModifier = styleObj && !PHOTO_VARIANT_STYLES.includes(styleObj.id)
        ? `RENDER STYLE: ${styleObj.prompt}`
        : styleObj && styleObj.id !== 'photorealistic'
        ? `PHOTO STYLE: ${styleObj.prompt}`
        : undefined;

      // If globe mode: capture 3D tiles from street level as guide image
      let overrideGuideImage: string | undefined;
      if (globeCapture) {
        console.log('[StreetViewPanel] Capturing 3D tiles from street level...');
        const captured = await globeCapture();
        if (captured) {
          overrideGuideImage = captured;
          console.log('[StreetViewPanel] 3D tiles capture successful');
        } else {
          console.warn('[StreetViewPanel] 3D tiles capture failed, falling back to clay render');
        }
      }

      const results = await Promise.all(STREET_VIEW_RENDER_MODELS.map(async (provider) => {
        try {
          const providerResult = await generateStreetView(
            pegmanPosition,
            pegmanAngle,
            siteZones,
            {
              model: provider.model,
              imageQuality: provider.imageQuality,
              previousRenderBase64,
              styleModifier,
              overrideGuideImage,
              projectId,
              useRealContext,
              includePeople,
              includeVehicles,
            },
          );
          return providerResult
            ? { ...providerResult, model: provider.model, imageQuality: provider.imageQuality, providerLabel: provider.label }
            : {
                imageUrl: createErrorPreviewImage(provider.label, 'The backend returned no image. Check backend logs for provider details.'),
                prompt: '',
                model: provider.model,
                imageQuality: provider.imageQuality,
                providerLabel: provider.label,
                error: 'The backend returned no image.',
              };
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Render failed. Check backend logs for provider details.';
          return {
            imageUrl: createErrorPreviewImage(provider.label, message),
            prompt: '',
            model: provider.model,
            imageQuality: provider.imageQuality,
            providerLabel: provider.label,
            error: message,
          };
        }
      }));

      if (results.length > 0) {
        setPreviews(results);
        const firstSuccessfulIndex = Math.max(0, results.findIndex((preview) => !preview.error));
        setSelectedPreviewIndex(firstSuccessfulIndex);
        setResult(results[firstSuccessfulIndex]);
        if (projectId) {
          Promise.allSettled(
            results
              .filter((preview) => !preview.error)
              .map((preview) => saveStreetViewRender(preview)),
          ).catch(() => undefined);
        }
        const failedLabels = results.filter((preview) => preview.error).map((preview) => preview.providerLabel || preview.model);
        if (failedLabels.length > 0) {
          toast.error(`${failedLabels.join(', ')} failed`);
        }
      } else {
        toast.error('Street view generation failed');
      }
    } catch (err) {
      console.error('[StreetViewPanel] Generation error:', err);
      toast.error('Street view generation failed');
    } finally {
      setIsGenerating(false);
    }
  }, [streetViewPegman, siteZones, generateStreetView, selectedStyle, useRealContext, includePeople, includeVehicles, result, globeCapture, projectId, saveStreetViewRender]);

  const handleDownload = useCallback(() => {
    if (!result?.imageUrl || result.error) return;
    const a = document.createElement('a');
    a.href = result.imageUrl;
    a.download = `siteforge-streetview-${Date.now()}.png`;
    a.click();
  }, [result]);

  const handleSave = useCallback(async () => {
    if (!result?.imageUrl || result.error || !projectId) return;
    setSaving(true);
    try {
      await saveStreetViewRender(result, true);
    } catch {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  }, [result, projectId, saveStreetViewRender]);

  const handleEditRender = useCallback(() => {
    if (!projectId || !result?.imageUrl || result.error) return;
    setLightboxOpen(false);
    setEditTarget(toEditableStreetViewRender(result));
  }, [projectId, result, toEditableStreetViewRender]);

  const handleEditedRenderSaved = useCallback((saved: SavedRender) => {
    const editedResult: StreetViewResult = {
      imageUrl: resolveApiFileUrl(saved.image_url),
      prompt: saved.prompt,
      model: saved.model,
      imageQuality: saved.image_quality,
      providerLabel: 'Edited Street View',
    };
    setResult(editedResult);
    setPreviews((current) => {
      if (selectedPreviewIndex === null) return current;
      return current.map((preview, index) => (
        index === selectedPreviewIndex ? editedResult : preview
      ));
    });
    setSavedImageKeys((prev) => new Set(prev).add(getRenderImageKey(editedResult)));
    onRenderSaved?.(saved);
  }, [onRenderSaved, selectedPreviewIndex]);

  const handleClose = useCallback(() => {
    setStreetViewPosition(null);
    setStreetViewActive(false);
    setResult(null);
    setPreviews([]);
    setSelectedPreviewIndex(null);
    setEditTarget(null);
  }, [setStreetViewPosition, setStreetViewActive]);

  // Don't render until Street View mode is active
  if (!streetViewPegman) return null;

  // Pegman mode is active but no pin has been dropped yet — show the "drop a pin" prompt.
  if (!streetViewPegman.position) {
    return (
      <div className="absolute bottom-4 left-1/2 z-40 -translate-x-1/2">
        <div className="street-view-card street-view-card--prompt flex items-center gap-3 rounded-lg px-4 py-3 backdrop-blur-xl">
          <span className="street-view-badge flex h-8 w-8 items-center justify-center rounded-full">
            <Eye size={16} />
          </span>
          <span className="text-sm font-black">
            Click on the map to drop a Street View pin
          </span>
          <button
            onClick={() => setStreetViewActive(false)}
            className="street-view-close-button street-view-close-button--small rounded-full p-1 transition"
            title="Cancel Street View"
          >
            <X size={14} />
          </button>
        </div>
      </div>
    );
  }

  // Full-screen modal when we have a result
  if (result) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div className="relative mx-4 flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl bg-gray-900 shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-white/10 px-5 py-3">
            <div className="flex items-center gap-2 text-white">
              <Eye size={18} className="text-amber-400" />
              <span className="font-semibold">
                Street View AI Render ({result.providerLabel || STREET_VIEW_RENDER_LABEL}) — Looking {compassLabel(streetViewPegman.angle)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {projectId && (
                <button
                  onClick={handleEditRender}
                  disabled={!!result.error}
                  className="flex items-center gap-1.5 rounded-lg bg-amber-400 px-3 py-1.5 text-sm font-bold text-black hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-50"
                  title="Edit masked area"
                  aria-label="Edit render"
                >
                  <Wand2 size={14} />
                  Edit Render
                </button>
              )}
              <button
                onClick={handleDownload}
                disabled={!!result.error}
                className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Download size={14} />
                Download PNG
              </button>
              {projectId && (
                <button
                  onClick={handleSave}
                  disabled={saving || !!result.error}
                  className="flex items-center gap-1.5 rounded-lg bg-emerald-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
                >
                  <Save size={14} />
                  {saving ? 'Saving...' : result && savedImageKeys.has(getRenderImageKey(result)) ? 'Saved' : 'Save'}
                </button>
              )}
              <button
                onClick={() => setResult(null)}
                className="rounded-lg p-1.5 text-white/60 hover:bg-white/10 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>
          </div>
          {/* Image — click to enlarge */}
          <div className="flex-1 overflow-auto p-4">
            <div className="relative">
              <img
                src={result.imageUrl}
                alt={`${result.providerLabel || 'Street view'} render`}
                className={`h-auto w-full rounded-lg transition ${result.error ? '' : 'cursor-pointer hover:opacity-90'}`}
                onClick={() => !result.error && setLightboxOpen(true)}
                title={result.error ? result.error : 'Click to enlarge'}
              />
              <span className={`pointer-events-none absolute left-3 top-3 rounded px-2 py-1 text-xs font-bold text-white ${result.error ? 'bg-red-500/90' : 'bg-black/70'}`}>
                {result.providerLabel || 'Street View'}
              </span>
            </div>
            {previews.length > 1 && (
              <div className="mt-3">
                <div className="mb-1 flex items-center justify-between text-[11px] text-white/50">
                  <span>{previews[selectedPreviewIndex ?? 0]?.providerLabel || 'Choose a render'}</span>
                  <span>{previews.length} provider test</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {previews.map((preview, index) => (
                    <button
                      key={preview.providerLabel || preview.model || index}
                      onClick={() => {
                        setSelectedPreviewIndex(index);
                        setResult(preview);
                      }}
                      className={`relative aspect-video overflow-hidden rounded-lg border-2 transition ${
                        preview.error
                          ? 'border-red-400/70 hover:border-red-300'
                          : selectedPreviewIndex === index
                            ? 'border-amber-400 ring-2 ring-amber-400/40'
                            : 'border-white/10 hover:border-white/40'
                      }`}
                      title={preview.error ? `${preview.providerLabel} failed: ${preview.error}` : `${preview.providerLabel} preview`}
                    >
                      <img
                        src={preview.imageUrl}
                        alt={`${preview.providerLabel || `Preview ${index + 1}`} render`}
                        className="h-full w-full object-cover"
                      />
                      <span className="pointer-events-none absolute left-1 top-1 max-w-[calc(100%-0.5rem)] truncate rounded bg-black/70 px-1.5 py-0.5 text-[10px] font-bold text-white">
                        {preview.providerLabel || `Preview ${index + 1}`}
                      </span>
                      {preview.error && (
                        <span className="pointer-events-none absolute bottom-1 left-1 rounded bg-red-500/90 px-1.5 py-0.5 text-[10px] font-bold text-white">
                          Failed
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          {/* Footer — re-render controls */}
          <div className="flex items-center justify-between border-t border-white/10 px-5 py-3">
            <div className="flex items-center gap-2">
              <button
                onClick={handleRotateLeft}
                className="rounded-lg bg-white/10 p-2 text-white hover:bg-white/20"
                title="Rotate left 45°"
              >
                <ArrowLeft size={16} />
              </button>
              <span className="min-w-[40px] text-center text-sm font-medium text-white">
                {compassLabel(streetViewPegman.angle)}
              </span>
              <button
                onClick={handleRotateRight}
                className="rounded-lg bg-white/10 p-2 text-white hover:bg-white/20"
                title="Rotate right 45°"
              >
                <ArrowRight size={16} />
              </button>
            </div>
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
            >
              {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Eye size={14} />}
              {isGenerating ? 'Rendering...' : 'Re-render Previews'}
            </button>
          </div>
        </div>

        {/* Lightbox modal — click image to enlarge */}
        {lightboxOpen && result && (
          <div
            className="fixed inset-0 z-[300] flex items-center justify-center bg-black/85 backdrop-blur-sm"
            onClick={() => setLightboxOpen(false)}
          >
            <div className="relative max-h-[90vh] max-w-[90vw]" onClick={(e) => e.stopPropagation()}>
              <img
                src={result.imageUrl}
                alt="Street view render"
                className="max-h-[85vh] max-w-full rounded-xl object-contain shadow-2xl"
              />
              <div className="absolute bottom-0 left-0 right-0 rounded-b-xl bg-gradient-to-t from-black/80 to-transparent px-4 py-3">
                <p className="text-xs text-white/80 line-clamp-2">{result.prompt}</p>
                <p className="mt-1 text-[10px] text-white/50">
                  {STREET_VIEW_STYLES.find(s => s.id === selectedStyle)?.label || selectedStyle} style
                  {streetViewPegman && ` · ${compassLabel(streetViewPegman.angle)}`}
                </p>
              </div>
              <button
                onClick={() => setLightboxOpen(false)}
                className="absolute top-3 right-3 rounded-full bg-black/60 p-2 text-white/80 hover:bg-black/80 hover:text-white transition"
              >
                <X size={20} />
              </button>
              <a
                href={result.imageUrl}
                download={`siteforge-streetview-${Date.now()}.png`}
                className="absolute top-3 right-14 rounded-full bg-black/60 p-2 text-white/80 hover:bg-black/80 hover:text-white transition"
                title="Download"
              >
                <Download size={20} />
              </a>
              {projectId && !result.error && (
                <button
                  type="button"
                  onClick={handleEditRender}
                  className="absolute right-28 top-3 flex items-center gap-2 rounded-full bg-amber-400 px-3 py-2 text-xs font-bold text-black shadow-lg shadow-black/30 ring-1 ring-white/20 transition hover:bg-amber-300"
                  title="Edit masked area"
                  aria-label="Edit render"
                >
                  <Wand2 size={16} />
                  Edit Render
                </button>
              )}
            </div>
          </div>
        )}
        {projectId && editTarget && (
          <RenderEditModal
            projectId={projectId}
            render={editTarget}
            imageUrl={editTarget.image_url}
            onSaved={handleEditedRenderSaved}
            onClose={() => setEditTarget(null)}
          />
        )}
      </div>
    );
  }

  // Floating panel on the map
  return (
    <div className="absolute bottom-4 left-1/2 z-40 w-[min(94vw,760px)] -translate-x-1/2">
      <div className="street-view-card street-view-card--panel flex flex-wrap items-center justify-center gap-3 rounded-lg px-4 py-3 backdrop-blur-xl">
        {/* Direction controls */}
        <button
          onClick={handleRotateLeft}
          className="street-view-icon-button flex h-9 w-9 items-center justify-center rounded-full transition"
          title="Rotate left 45 degrees"
        >
          <ArrowLeft size={16} />
        </button>

        {/* Compass */}
        <div className="flex flex-col items-center">
          <div
            className="street-view-compass relative flex h-12 w-12 items-center justify-center rounded-full"
          >
            <div
              className="street-view-compass-needle absolute h-5 w-0.5 origin-bottom"
              style={{
                transform: `rotate(${streetViewPegman.angle}deg)`,
                bottom: '50%',
              }}
            />
            <span className="text-[10px] font-black">
              {compassLabel(streetViewPegman.angle)}
            </span>
          </div>
          <span className="street-view-helper mt-1 text-[9px] font-black uppercase">
            Rotate
          </span>
        </div>

        <button
          onClick={handleRotateRight}
          className="street-view-icon-button flex h-9 w-9 items-center justify-center rounded-full transition"
          title="Rotate right 45 degrees"
        >
          <ArrowRight size={16} />
        </button>

        {/* Divider */}
        <div className="street-view-divider hidden h-16 w-px sm:block" />

        {/* Style selector */}
        <div className="street-view-style-list max-h-36 min-w-[220px] flex-1 overflow-y-auto rounded-lg p-2">
          {STREET_VIEW_STYLE_GROUPS.map(group => (
            <div key={group.label}>
              <div className="street-view-group-label mb-1 text-[9px] font-black uppercase tracking-wider">{group.label}</div>
              <div className="mb-2 flex flex-wrap gap-1.5 last:mb-0">
                {group.ids.map(id => {
                  const s = STREET_VIEW_STYLES.find(x => x.id === id);
                  if (!s) return null;
                  return (
                    <button
                      key={s.id}
                      onClick={() => setSelectedStyle(s.id)}
                      className={`street-view-style-pill rounded-full px-2.5 py-1 text-[10px] font-black uppercase transition ${
                        selectedStyle === s.id
                          ? 'street-view-style-pill--active'
                          : 'street-view-style-pill--idle'
                      }`}
                    >
                      {s.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Real-world context toggle */}
        <label className="flex max-w-[150px] cursor-pointer items-center gap-2 text-[10px] font-black uppercase leading-tight text-[#151515]">
          <input
            type="checkbox"
            checked={useRealContext}
            onChange={(e) => setUseRealContext(e.target.checked)}
            className="h-3.5 w-3.5 shrink-0 accent-[#c9ff3d]"
          />
          <span>
            Real site context
            <br />
            (Google Street View API)
          </span>
        </label>

        {/* Add people / vehicles toggles — default off for clean hero renders */}
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            onClick={() => setIncludePeople((v) => !v)}
            className={`rounded-full px-3 py-1.5 text-[10px] font-black uppercase leading-tight transition ${
              includePeople ? 'bg-[#c9ff3d] text-[#151515]' : 'bg-black/5 text-[#151515]/55 hover:bg-black/10'
            }`}
          >
            {includePeople ? '✓ People' : 'Add People'}
          </button>
          <button
            type="button"
            onClick={() => setIncludeVehicles((v) => !v)}
            className={`rounded-full px-3 py-1.5 text-[10px] font-black uppercase leading-tight transition ${
              includeVehicles ? 'bg-[#c9ff3d] text-[#151515]' : 'bg-black/5 text-[#151515]/55 hover:bg-black/10'
            }`}
          >
            {includeVehicles ? '✓ Vehicles' : 'Add Vehicles'}
          </button>
        </div>

        {/* Divider */}
        <div className="street-view-divider hidden h-16 w-px sm:block" />

        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="street-view-generate-button flex min-h-12 items-center gap-2 rounded-full px-5 py-3 text-sm font-black uppercase transition disabled:opacity-50"
        >
          {isGenerating ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Rendering {STREET_VIEW_RENDER_LABEL}
            </>
          ) : (
            <>
              <Eye size={16} />
              Render
            </>
          )}
        </button>

        {/* Close */}
        <button
          onClick={handleClose}
          className="street-view-close-button flex h-8 w-8 items-center justify-center rounded-full transition"
          title="Close street view"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
