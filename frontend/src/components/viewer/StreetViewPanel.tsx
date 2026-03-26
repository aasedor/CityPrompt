/**
 * StreetViewPanel — floating panel that appears when the street view pegman
 * is placed on the map. Shows compass direction, rotation controls, and a
 * generate button. Displays the rendered street view in a modal.
 */
import { useState, useCallback } from 'react';
import { Eye, ArrowLeft, ArrowRight, Loader2, X, Download, Save } from 'lucide-react';
import { useViewerStore } from '@/store';
import { useStreetViewRender } from './useStreetViewRender';
import type { SiteZone } from '@/types';
import { rendersApi } from '@/services/api';
import toast from 'react-hot-toast';

const COMPASS_LABELS: Record<number, string> = {
  0: 'N', 45: 'NE', 90: 'E', 135: 'SE',
  180: 'S', 225: 'SW', 270: 'W', 315: 'NW',
};

const STREET_VIEW_STYLES = [
  {
    id: 'photorealistic',
    label: 'Photo',
    prompt: 'Hyper-photorealistic street-level architectural visualization. Camera positioned at exact human eye-level using a 35mm prime lens at f/8 aperture ensuring deep focus and edge-to-edge sharpness. Golden hour on a clear day with warm low-angle directional sunlight casting long crisp high-contrast shadows across the sidewalk. Subtle hyper-realistic environmental details: specular reflections of adjacent buildings visible in glass facades, slight atmospheric haze, photorealistic street trees. Rendered in the style of Unreal Engine 5 with path-traced global illumination, 8K resolution, architectural digest photography.',
  },
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
    id: 'risograph',
    label: 'Risograph',
    prompt: 'A two-colour risograph print of the architectural streetscape on uncoated recycled kraft paper with visible flecks and warm tan base tone. Printed in exactly two flat spot-ink colours -- a warm coral-vermilion and a deep teal-indigo -- that overlap to create a limited palette of four tones including the raw paper and the dark near-black where both inks overprint. Characteristic visible halftone dot patterns at varied densities create all tonal gradation. Deliberate slight misregistration between the two colour passes creates a charming offset where colour edges do not perfectly align producing a vibrant double-exposure effect on building edges and window frames. Ink coverage is intentionally uneven with subtle streaks and grain from the stencil drum. Flat graphic aesthetic with no photorealistic shading or gradients -- all depth achieved through halftone density and colour layering. Bold simplified architectural forms. Independent zine aesthetic, small-press graphic design, contemporary editorial illustration, limited-edition art print.',
  },
  {
    id: 'gouache',
    label: 'Gouache',
    prompt: 'A vibrant opaque gouache architectural painting on toned warm grey illustration board. The painting style features bold flat areas of thick matte opaque colour with clearly visible brushstroke edges and slight paint texture where the brush has dragged across the board surface. Unlike transparent watercolour, all paint layers are fully opaque and cover underlying colours completely -- shadows are painted with mixed dark pigments not translucent washes. Colour palette is vivid and saturated but carefully harmonized -- rich terracotta and salmon for sunlit facades, deep navy and prussian blue for shadow sides, bright cadmium yellow and warm orange for awnings and signage, muted sage and forest green for vegetation. Each colour area is rendered as a confident decisive shape with minimal blending between adjacent hues creating a bold graphic patchwork effect. Highlights painted with thick strokes of pure titanium white mixed with a hint of warm yellow. The toned grey board visible at unpainted edges. Mid-century travel poster aesthetic, Bauhaus design school illustration, WPA Federal Art Project architectural painting, exhibition quality.',
  },
  {
    id: 'pixel-art',
    label: 'Pixel Art',
    prompt: 'A detailed pixel art architectural scene of the streetscape rendered at a fixed resolution of approximately 320x240 pixels then scaled up with nearest-neighbour interpolation preserving crisp hard pixel edges with absolutely no anti-aliasing or smoothing. Every element is constructed from clearly visible individual square pixels in a carefully curated limited palette of no more than 32 colours. Buildings are depicted with pixel-perfect geometric precision -- each window is a consistent small rectangle of uniform dark pixels, each brick course suggested by alternating pixel rows. Deliberate dithering patterns using alternating pixel colours to create intermediate tones and textures on facades. Trees are stylized as rounded clusters of green-toned pixels. Dramatic pixel-art lighting with a clear warm directional light source creating crisp one-pixel-wide shadow edges. The ground plane features clean perspective lines constructed from stepped pixel diagonals. 16-bit era video game aesthetic, retro SNES city background, demoscene art, nostalgic digital craftsmanship.',
  },
] as const;

function compassLabel(angle: number): string {
  const norm = ((angle % 360) + 360) % 360;
  return COMPASS_LABELS[norm] || `${norm}°`;
}

interface StreetViewPanelProps {
  siteZones: SiteZone[];
  projectId?: string;
}

export function StreetViewPanel({ siteZones, projectId }: StreetViewPanelProps) {
  const { streetViewPegman, setStreetViewAngle, setStreetViewPosition, setStreetViewActive } = useViewerStore();
  const { generateStreetView } = useStreetViewRender();
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<{ imageUrl: string; prompt: string } | null>(null);
  const [saving, setSaving] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');

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
    setIsGenerating(true);
    try {
      // For re-renders: extract previous render base64 for dual anchoring
      let previousRenderBase64: string | undefined;
      if (result?.imageUrl?.startsWith('data:image/')) {
        previousRenderBase64 = result.imageUrl.split(',')[1];
      }

      const styleObj = STREET_VIEW_STYLES.find(s => s.id === selectedStyle);
      const styleModifier = styleObj && styleObj.id !== 'photorealistic'
        ? `RENDER STYLE: ${styleObj.prompt}`
        : undefined;

      const res = await generateStreetView(
        streetViewPegman.position,
        streetViewPegman.angle,
        siteZones,
        {
          model: selectedModel !== 'gemini-2.5-flash-image' ? selectedModel : undefined,
          previousRenderBase64,
          styleModifier,
        },
      );
      if (res) {
        setResult(res);
      } else {
        toast.error('Street view generation failed');
      }
    } catch (err) {
      console.error('[StreetViewPanel] Generation error:', err);
      toast.error('Street view generation failed');
    } finally {
      setIsGenerating(false);
    }
  }, [streetViewPegman, siteZones, generateStreetView, selectedModel, selectedStyle, result]);

  const handleDownload = useCallback(() => {
    if (!result?.imageUrl) return;
    const a = document.createElement('a');
    a.href = result.imageUrl;
    a.download = `siteforge-streetview-${Date.now()}.png`;
    a.click();
  }, [result]);

  const handleSave = useCallback(async () => {
    if (!result?.imageUrl || !projectId) return;
    setSaving(true);
    try {
      const b64 = result.imageUrl.replace(/^data:image\/\w+;base64,/, '');
      await rendersApi.save(projectId, {
        image_base64: b64,
        prompt: result.prompt,
        style: 'street-view',
      });
      toast.success('Street view saved');
    } catch {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  }, [result, projectId]);

  const handleClose = useCallback(() => {
    setStreetViewPosition(null);
    setStreetViewActive(false);
    setResult(null);
  }, [setStreetViewPosition, setStreetViewActive]);

  // Don't render if pegman is not placed
  if (!streetViewPegman?.position) return null;

  // Full-screen modal when we have a result
  if (result) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div className="relative mx-4 flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl bg-gray-900 shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-white/10 px-5 py-3">
            <div className="flex items-center gap-2 text-white">
              <Eye size={18} className="text-amber-400" />
              <span className="font-semibold">Street View — Looking {compassLabel(streetViewPegman.angle)}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-600"
              >
                <Download size={14} />
                Download PNG
              </button>
              {projectId && (
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-1.5 rounded-lg bg-emerald-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
                >
                  <Save size={14} />
                  {saving ? 'Saving...' : 'Save'}
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
          {/* Image */}
          <div className="flex-1 overflow-auto p-4">
            <img
              src={result.imageUrl}
              alt="Street view render"
              className="h-auto w-full rounded-lg"
            />
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
              Re-render
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Floating panel on the map
  return (
    <div className="absolute bottom-4 left-1/2 z-40 -translate-x-1/2">
      <div className="flex items-center gap-3 rounded-xl bg-white/95 px-4 py-3 shadow-2xl backdrop-blur-sm">
        {/* Direction controls */}
        <button
          onClick={handleRotateLeft}
          className="rounded-lg bg-primary-950/[0.06] p-2 text-primary-950/70 hover:bg-primary-950/[0.12] hover:text-primary-950"
          title="Rotate left 45° (← arrow key)"
        >
          <ArrowLeft size={16} />
        </button>

        {/* Compass */}
        <div className="flex flex-col items-center">
          <div
            className="relative flex h-12 w-12 items-center justify-center rounded-full border-2 border-amber-400 bg-amber-50"
          >
            <div
              className="absolute h-5 w-0.5 bg-amber-500 origin-bottom"
              style={{
                transform: `rotate(${streetViewPegman.angle}deg)`,
                bottom: '50%',
              }}
            />
            <span className="text-[10px] font-bold text-amber-700">
              {compassLabel(streetViewPegman.angle)}
            </span>
          </div>
          <span className="mt-1 text-[10px] text-primary-950/50">
            ← → to rotate
          </span>
        </div>

        <button
          onClick={handleRotateRight}
          className="rounded-lg bg-primary-950/[0.06] p-2 text-primary-950/70 hover:bg-primary-950/[0.12] hover:text-primary-950"
          title="Rotate right 45° (→ arrow key)"
        >
          <ArrowRight size={16} />
        </button>

        {/* Divider */}
        <div className="h-8 w-px bg-primary-950/10" />

        {/* Model selector */}
        <div className="flex flex-col gap-0.5">
          {[
            { id: 'gemini-2.5-flash-image', label: '2.5' },
            { id: 'gemini-3.1-flash-image-preview', label: '3.1' },
            { id: 'gemini-3-pro-image-preview', label: 'Pro' },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setSelectedModel(m.id)}
              className={`rounded px-2 py-0.5 text-[10px] font-medium transition ${
                selectedModel === m.id
                  ? 'bg-blue-500/20 text-blue-600'
                  : 'text-primary-950/40 hover:bg-primary-950/[0.06] hover:text-primary-950/70'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="h-8 w-px bg-primary-950/10" />

        {/* Style selector */}
        <div className="flex flex-col gap-0.5">
          {STREET_VIEW_STYLES.map((s) => (
            <button
              key={s.id}
              onClick={() => setSelectedStyle(s.id)}
              className={`rounded px-2 py-0.5 text-[10px] font-medium transition ${
                selectedStyle === s.id
                  ? 'bg-amber-500/20 text-amber-700'
                  : 'text-primary-950/40 hover:bg-primary-950/[0.06] hover:text-primary-950/70'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="h-8 w-px bg-primary-950/10" />

        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex items-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-amber-600 disabled:opacity-50 transition-all"
        >
          {isGenerating ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Eye size={16} />
              Generate Street View
            </>
          )}
        </button>

        {/* Close */}
        <button
          onClick={handleClose}
          className="rounded-lg p-1.5 text-primary-950/40 hover:bg-primary-950/[0.06] hover:text-primary-950"
          title="Close street view"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
