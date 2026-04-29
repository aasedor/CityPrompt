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
    prompt: 'Cinematic street-level architectural photograph emphasizing dramatic atmospheric conditions and emotional lighting. Camera at human eye height, 50mm lens, f/2.8 with shallow depth of field -- foreground architectural details tack-sharp while the distant streetscape dissolves into soft atmospheric bokeh. The scene is captured during blue hour, approximately 20 minutes after sunset. The sky transitions from deep indigo overhead through bands of magenta and burnt orange at the horizon. All ambient exterior light is cool blue-violet while interior lights glow intensely warm amber and gold through floor-to-ceiling glazing, creating strong warm-cool colour temperature contrast that defines every window bay and entrance. Recent rainfall has left the entire street surface wet -- pavement, sidewalks, and plaza surfaces act as dark mirrors reflecting the glowing building facades, the coloured sky gradient, and the amber pools of light spilling from ground-floor retail. Shallow puddles collected in slight pavement depressions create concentrated reflections. Subtle volumetric moisture visible in the air around exterior light sources, creating soft haloes and gentle god rays where interior light spills outward through entrance lobbies. Building materials respond to the wet conditions -- concrete darkened two shades, brushed stainless steel panels showing streaky water rivulets, timber cladding saturated to a richer tone. Atmospheric perspective compresses the background -- distant buildings reduced to cool blue-grey silhouettes with pinpoints of warm window light. Thin wisps of low cloud or mist drifting at rooftop level. The mood is contemplative, cinematic, and deeply atmospheric -- this is an award-winning architectural photograph, not a technical documentation image.',
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

function compassLabel(angle: number): string {
  const norm = ((angle % 360) + 360) % 360;
  return COMPASS_LABELS[norm] || `${norm}°`;
}

interface StreetViewPanelProps {
  siteZones: SiteZone[];
  projectId?: string;
  /** When provided, captures 3D tiles from street level instead of clay render */
  globeCapture?: () => Promise<string | null>;
}

export function StreetViewPanel({ siteZones, projectId, globeCapture }: StreetViewPanelProps) {
  const { streetViewPegman, setStreetViewAngle, setStreetViewPosition, setStreetViewActive } = useViewerStore();
  const { generateStreetView } = useStreetViewRender();
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<{ imageUrl: string; prompt: string } | null>(null);
  const [saving, setSaving] = useState(false);
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');
  const [lightboxOpen, setLightboxOpen] = useState(false);

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

      const res = await generateStreetView(
        streetViewPegman.position,
        streetViewPegman.angle,
        siteZones,
        {
          previousRenderBase64,
          styleModifier,
          overrideGuideImage,
          projectId,
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
  }, [streetViewPegman, siteZones, generateStreetView, selectedStyle, result, globeCapture, projectId]);

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

  // Don't render until Street View mode is active
  if (!streetViewPegman) return null;

  // Pegman mode is active but no pin has been dropped yet — show the "drop a pin" prompt.
  if (!streetViewPegman.position) {
    return (
      <div className="absolute bottom-4 left-1/2 z-40 -translate-x-1/2">
        <div className="flex items-center gap-3 rounded-xl bg-white/95 px-4 py-3 shadow-2xl backdrop-blur-sm">
          <Eye size={16} className="text-amber-600" />
          <span className="text-sm font-medium text-primary-950">
            Click on the map to drop a Street View pin
          </span>
          <button
            onClick={() => setStreetViewActive(false)}
            className="rounded-lg p-1 text-primary-950/50 transition hover:bg-primary-950/[0.08] hover:text-primary-950"
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
          {/* Image — click to enlarge */}
          <div className="flex-1 overflow-auto p-4">
            <img
              src={result.imageUrl}
              alt="Street view render"
              className="h-auto w-full cursor-pointer rounded-lg transition hover:opacity-90"
              onClick={() => setLightboxOpen(true)}
              title="Click to enlarge"
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
            </div>
          </div>
        )}
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

        {/* Style selector */}
        <div className="flex flex-col gap-1.5">
          {STREET_VIEW_STYLE_GROUPS.map(group => (
            <div key={group.label}>
              <div className="mb-0.5 text-[9px] font-semibold uppercase tracking-wider text-primary-950/30">{group.label}</div>
              <div className="flex flex-col gap-0.5">
                {group.ids.map(id => {
                  const s = STREET_VIEW_STYLES.find(x => x.id === id);
                  if (!s) return null;
                  return (
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
                  );
                })}
              </div>
            </div>
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
