import streetViewStylePresets from '@/data/streetViewStylePresets.json';
import {AnimateRenderButton} from './AnimateRenderButton';
/**
 * StreetViewPanel — floating panel that appears when the street view pegman
 * is placed on the map. Shows compass direction, rotation controls, and a
 * generate button. Displays the rendered street view in a modal.
 */
import { useState, useCallback, useMemo } from 'react';
import { Eye, ArrowLeft, ArrowRight, Loader2, X, Download, Save, Wand2 } from 'lucide-react';
import { useViewerStore } from '@/store';
import {
  useStreetViewRender,
  type StreetCaptureResult,
  type StreetViewGuideKind,
  type StreetViewResult,
} from './useStreetViewRender';
import type { Building, SavedRender, SiteZone } from '@/types';
import toast from 'react-hot-toast';
import { getRenderImageKey, saveRenderedImage } from '@/utils/renderPersistence';
import { downloadImage } from '@/utils/downloadDataImage';
import { getApiErrorMessage, resolveApiFileUrl } from '@/services/api';
import { RenderEditModal } from './RenderEditModal';
import { DIRECT_3D_ALLOWED_STYLES, resolveDirect3DPresentationMode, useDirect3DRender } from './globe/useDirect3DRender';
import { collectDirect3DArchetypeReferences } from './globe/direct3dArchetypeReferences';
import { getCommunity3DCaptureClaims } from '@/features/community3d/community3d';
import { getCurrentResidualLandscapeClaim } from './globe/residualLandscape';
import { DEFAULT_OPENAI_IMAGE_MODEL, imageModelLabel, imageModelsForChoice, isLocalImageModel, imageModelUnavailable } from '@/config/imageModels';
import { renderLocalImage } from '@/services/localImageRender';
import { ImageModelSelect } from './ImageModelSelect';
import { useImageModelChoice } from './useImageModelChoice';
import { runImageModelBatch } from './runImageModelBatch';
import { RenderStyleGuideButton } from './RenderStyleGuideButton';

const COMPASS_LABELS: Record<number, string> = {
  0: 'N', 45: 'NE', 90: 'E', 135: 'SE',
  180: 'S', 225: 'SW', 270: 'W', 315: 'NW',
};

const STREET_VIEW_STYLES: ReadonlyArray<{ readonly id: string; readonly label: string; readonly prompt: string }> = streetViewStylePresets;

// UI grouping for the style picker — Plan group omitted because street view
// excludes orthographic styles by design.
const STREET_VIEW_STYLE_GROUPS = [
  { label: 'Realistic', ids: ['photorealistic', 'photomontage', 'atmospheric', 'winter'] },
  { label: 'Accurate', ids: ['survey', 'documentary', 'human-scale'] },
  { label: 'Concept', ids: ['watercolour', 'charcoal', 'marker-render', 'pen-and-ink'] },
  { label: 'Stylized', ids: ['clay-model', 'collage', 'pixel-art'] },
] as const;

const STREET_VIEW_RENDER_MODELS = [
  { model: DEFAULT_OPENAI_IMAGE_MODEL, label: imageModelLabel(DEFAULT_OPENAI_IMAGE_MODEL), imageQuality: 'auto' as const },
  { model: 'gpt-image-2.5-flare', label: imageModelLabel('gpt-image-2.5-flare'), imageQuality: 'auto' as const },
  { model: 'gpt-image-2.5-sunburst', label: imageModelLabel('gpt-image-2.5-sunburst'), imageQuality: 'auto' as const },
];
const STREET_VIEW_RENDER_LABEL = 'Gemini + GPT Image';

// Street style ids that don't exist verbatim in the Direct 3D catalogue.
const STREET_TO_DIRECT3D_STYLE: Record<string, string> = {
  'human-scale': 'photorealistic',
  'clay-model': 'clay-maquette',
};

function resolveDirect3DStreetStyle(streetStyleId: string): string {
  const mapped = STREET_TO_DIRECT3D_STYLE[streetStyleId] ?? streetStyleId;
  return DIRECT_3D_ALLOWED_STYLES.has(mapped) ? mapped : 'photorealistic';
}

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
  detailsRevision?: number;
  /** When provided, captures the globe scene from street level instead of the
   *  clay render — including the authored 3D building models when present
   *  (result.kind tells which framing the prompt should use). */
  globeCapture?: () => Promise<StreetCaptureResult | null>;
  /** Project buildings — required for the inventory-locked Direct 3D street
   *  path (per-zone capture claims are derived from them). */
  buildings?: Building[];
  onRenderSaved?: (render: SavedRender) => void;
  onPrepareCommunity3D?: () => void;
}

export function StreetViewPanel({ siteZones, projectId, detailsRevision, globeCapture, buildings, onRenderSaved, onPrepareCommunity3D }: StreetViewPanelProps) {
  const { streetViewPegman, setStreetViewAngle, setStreetViewPosition, setStreetViewActive } = useViewerStore();
  const { generateStreetView } = useStreetViewRender();
  const { renderDirect3D } = useDirect3DRender();
  // Inventory-locked single-call street render through the Direct 3D endpoint
  // (review-first). Off = the classic three-model flow.
  const [directStreetMode, setDirectStreetMode] = useState(Boolean(globeCapture));
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<StreetViewResult | null>(null);
  const [previews, setPreviews] = useState<StreetViewResult[]>([]);
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedRendersByImage,setSavedRendersByImage] = useState<Record<string,SavedRender>>({});
  const [savedImageKeys, setSavedImageKeys] = useState<Set<string>>(() => new Set());
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');
  const [customPrompt, setCustomPrompt] = useState('');
  // A street view starts with one image call; comparisons are an explicit choice.
  const { imageModel, setImageModel, availability: imageModelAvailability } = useImageModelChoice({ compareByDefault: false, projectId });
  const selectedEngineUnavailable = imageModelsForChoice(imageModel).some(model => imageModelUnavailable(imageModelAvailability, model));
  const [imageProgress, setImageProgress] = useState('');
  const [lightboxOpen, setLightboxOpen] = useState(false);
  // Real Street View / Places / satellite grounding, anchored at the pegman.
  // On by default (it helps); toggle off to A/B against a context-free render.
  const [useRealContext, setUseRealContext] = useState(true);
  const [includePeople, setIncludePeople] = useState(false);
  const [includeVehicles, setIncludeVehicles] = useState(false);
  const [editTarget, setEditTarget] = useState<SavedRender | null>(null);
  const [sourcePreview, setSourcePreview] = useState<{ imageUrl: string; position: string; angle: number } | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const currentSceneClaims = useMemo(
    () => globeCapture ? getCommunity3DCaptureClaims(siteZones, buildings ?? []) : null,
    [globeCapture, siteZones, buildings],
  );
  const needsCommunity3D = Boolean(directStreetMode && globeCapture && (!currentSceneClaims || (!currentSceneClaims.length && detailsRevision === undefined)));
  const previewStreetSource = async () => {
    if (!globeCapture || !streetViewPegman?.position || isPreviewing) return;
    const position = JSON.stringify(streetViewPegman.position);
    const angle = streetViewPegman.angle;
    setIsPreviewing(true);
    try {
      const source = await globeCapture();
      if (!source) throw new Error('The 3D view is not ready. Wait for the scene to load.');
      setSourcePreview({
        imageUrl: source.imageBase64.startsWith('data:') ? source.imageBase64 : `data:image/png;base64,${source.imageBase64}`,
        position, angle,
      });
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Could not preview this street view.'));
    } finally { setIsPreviewing(false); }
  };

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
    setSavedRendersByImage(previous=>({...previous,[key]:saved}));
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
    if (directStreetMode && selectedEngineUnavailable) {
      toast.error('Your selected image engine is unavailable. Choose an available engine.');
      return;
    }
    if (directStreetMode && (!currentSceneClaims || (!currentSceneClaims.length && detailsRevision === undefined))) {
      toast.error('Wait for the automatic 3D update before rendering this street view.');
      return;
    }
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

      // If globe mode: capture the 3D scene from street level as guide image.
      // kind === 'model3d' means the authored 3D building models are in frame;
      // 'context3d' means existing tiles + zone overlays only.
      let overrideGuideImage: string | undefined;
      let overrideGuideKind: StreetViewGuideKind | undefined;
      let overrideAspectRatio: string | undefined;
      let overrideSemanticGuide: string | undefined;
      let streetCapture: StreetCaptureResult | null = null;
      if (globeCapture) {
        console.log('[StreetViewPanel] Capturing globe scene from street level...');
        streetCapture = await globeCapture();
        if (streetCapture) {
          overrideGuideImage = streetCapture.imageBase64;
          overrideGuideKind = streetCapture.kind;
          overrideAspectRatio = streetCapture.aspectRatio;
          overrideSemanticGuide = streetCapture.semanticBase64;
          console.log(`[StreetViewPanel] Street-level capture successful (${streetCapture.kind}, ${streetCapture.aspectRatio}, semantic=${!!streetCapture.semanticBase64})`);
        } else {
          console.warn('[StreetViewPanel] Street-level capture is not ready');
        }
      }

      if (globeCapture && !streetCapture?.direct3d && !overrideGuideImage?.trim()) {
        toast('The street view is still loading. Try again when the scene is visible.');
        return;
      }
      if (directStreetMode && !projectId) {
        toast.error('Save the project before a street render.');
        return;
      }

      // Inventory-locked street render: one call through the Direct 3D
      // endpoint with the full pass stack. The server saves both the returned
      // view and any separate AI attempt; neither bypasses visual review.
      if (directStreetMode && projectId && streetCapture?.direct3d) {
        const bundle = streetCapture.direct3d;
        const claims = currentSceneClaims!;
        const directLabel = 'Direct 3D Street';
        const completedPreviews: StreetViewResult[] = [];
        try {
          const directStyle = resolveDirect3DStreetStyle(selectedStyle);
          const archetypeReferences = resolveDirect3DPresentationMode(directStyle) === 'scene'
            ? []
            : await collectDirect3DArchetypeReferences(siteZones, 8, bundle);
          await runImageModelBatch(imageModel, (model) => renderDirect3D(bundle, {
            model,
            style: directStyle,
            projectId,
            community3DClaims: claims,
            detailsRevision,
            residualLandscapeClaim: getCurrentResidualLandscapeClaim(siteZones),
            viewMode: 'street',
            archetypeReferences,
            customPrompt: [
              includePeople ? 'Include a few pedestrians on existing walking surfaces.' : 'Do not add people.',
              includeVehicles ? 'Include a few vehicles on existing carriageways only.' : 'Do not add vehicles.',
              includePeople ? 'Scale people using nearby doors and storeys. Show natural walking or seated poses with believable ground contact; keep feet visible when the captured framing allows. Respect occlusion by existing trees, buildings and furniture, and keep entrances and crossings readable.' : '',
              customPrompt.trim(),
              'Keep all buildings, facilities, paths and streets in their captured positions.',
            ].filter(Boolean).join(' '),
          }), (direct) => {
            const directResult: StreetViewResult = {
              imageUrl: direct.render.imageUrl,
              prompt: direct.render.prompt,
              model: direct.render.model,
              imageQuality: 'high',
              providerLabel: direct.render.providerLabel,
              reviewWarnings: direct.warnings,
            };
            const original = direct.providerOriginalRender;
            const originalPreview: StreetViewResult | undefined = original ? {
              imageUrl: resolveApiFileUrl(original.image_url),
              prompt: original.prompt,
              model: original.model,
              imageQuality: original.image_quality,
              providerLabel: 'AI render',
              reviewWarnings: ['AI original — compare its geometry with the clean 3D source.'],
            } : undefined;
            const sourcePreview: StreetViewResult = {
              imageUrl: direct.sourceImageUrl, prompt: '', providerLabel: 'Original 3D view',
            };
            const showingOriginal = direct.render.savedRender?.id === original?.id && Boolean(original);
            setSavedRendersByImage(previous=>({...previous,
              ...(direct.render.savedRender?{[getRenderImageKey(directResult)]:direct.render.savedRender}:{}),
              ...(original&&originalPreview?{[getRenderImageKey(originalPreview)]:original}:{}),
            }));
            const index = completedPreviews.length;
            completedPreviews.push(directResult);
            if (originalPreview && !showingOriginal) completedPreviews.push(originalPreview);
            completedPreviews.push(sourcePreview);
            setPreviews([...completedPreviews]);
            setSelectedPreviewIndex(index);
            setResult(directResult);
            // The endpoint already saves both outputs. Notify the gallery and
            // mark their preview keys so Save cannot create duplicate records.
            if (direct.render.savedRender) onRenderSaved?.(direct.render.savedRender);
            if (original && !showingOriginal) onRenderSaved?.(original);
            setSavedImageKeys((previous) => new Set([
              ...previous,
              ...(direct.render.savedRender ? [getRenderImageKey(directResult)] : []),
              ...(originalPreview ? [getRenderImageKey(originalPreview)] : []),
            ]));
            if (direct.outcome === 'review_required') {
              toast('Render saved. The 3D view is available for comparison.', { icon: '✓' });
            }
          }, (model, index, total) => setImageProgress(`${index + 1}/${total} · ${imageModelLabel(model)}`));
        } catch (err) {
          const message = getApiErrorMessage(err, 'Direct 3D street render failed.');
          const errorResult: StreetViewResult = {
            imageUrl: createErrorPreviewImage(directLabel, message),
            prompt: '',
            providerLabel: directLabel,
            error: message,
          };
          setPreviews([...completedPreviews, errorResult]);
          if (!completedPreviews.length) {
            setSelectedPreviewIndex(0);
            setResult(errorResult);
          }
          toast.error(`${directLabel} failed`);
        } finally {
          setImageProgress('');
        }
        return;
      }

      // A valid screenshot can still guide a render when auxiliary geometry
      // passes are unavailable. Select this before submission, never as a paid
      // provider retry, and honour the user's engine choice and call count.
      const providers = directStreetMode
        ? imageModelsForChoice(imageModel).map(model => ({
          model, label: `${imageModelLabel(model)} · Image-guided`, imageQuality: 'auto' as const,
        }))
        : STREET_VIEW_RENDER_MODELS;
      const results: StreetViewResult[] = await Promise.all(providers.map(async (provider) => {
        try {
          if (isLocalImageModel(provider.model)) {
            if (!projectId || !overrideGuideImage) throw new Error('The saved project and street view must be ready.');
            const prompt = [styleObj?.prompt,
              includePeople ? 'Include a few naturally posed pedestrians.' : 'Do not add people.',
              includeVehicles ? 'Include vehicles on existing streets.' : 'Do not add vehicles.',
              customPrompt.trim(),
            ].filter(Boolean).join(' ').slice(0, 1500);
            const saved = await renderLocalImage({ projectId, model: provider.model, imageBase64: overrideGuideImage, prompt });
            const preview = { imageUrl: resolveApiFileUrl(saved.image_url), prompt, model: provider.model,
              imageQuality: provider.imageQuality, providerLabel: provider.label };
            onRenderSaved?.(saved);
            setSavedImageKeys(previous => new Set(previous).add(getRenderImageKey(preview)));
            setSavedRendersByImage(previous=>({...previous,[getRenderImageKey(preview)]:saved}));
            return preview;
          }
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
              guideKind: overrideGuideKind,
              aspectRatio: overrideAspectRatio,
              semanticGuideBase64: overrideSemanticGuide,
              projectId,
              useRealContext,
              includePeople,
              includeVehicles,
              customPrompt: customPrompt.trim() || undefined,
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
              .filter((preview) => !preview.error && !isLocalImageModel(preview.model ?? ''))
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
  }, [streetViewPegman, siteZones, generateStreetView, renderDirect3D, directStreetMode, currentSceneClaims, detailsRevision, selectedStyle, imageModel, useRealContext, includePeople, includeVehicles, customPrompt, result, globeCapture, projectId, saveStreetViewRender, onRenderSaved, selectedEngineUnavailable]);

  const handleDownload = useCallback(async () => {
    if (!result?.imageUrl || result.error) return;
    try {
      await downloadImage(result.imageUrl, `siteforge-streetview-${Date.now()}.png`);
    } catch {
      toast.error('Could not download the image. Please try again.');
    }
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
    setSavedRendersByImage(previous=>({...previous,[getRenderImageKey(editedResult)]:saved}));
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
            <div className="flex flex-wrap items-center gap-2">
              {projectId && !result.error && savedRendersByImage[getRenderImageKey(result)] && <AnimateRenderButton projectId={projectId} render={savedRendersByImage[getRenderImageKey(result)]}/>}
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
            {Boolean(result.reviewWarnings?.length) && (
              <details className="mb-3 rounded-lg border border-amber-300/30 bg-amber-300/10 p-3 text-xs text-amber-100">
                <summary className="cursor-pointer font-semibold">Compare with the 3D source</summary>
                <ul className="mt-2 list-disc space-y-1 pl-4">
                  {result.reviewWarnings!.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </details>
            )}
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
                  <span>{previews.length} views</span>
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
          <div className="border-t border-white/10 px-5 py-3">
            <label htmlFor="street-render-custom-prompt" className="mb-1 block text-xs font-medium text-white">Custom prompt <span className="text-white/50">(optional)</span></label>
            <textarea
              spellCheck={true}
              lang="en-CA"
              id="street-render-custom-prompt"
              value={customPrompt}
              onChange={(event) => setCustomPrompt(event.target.value)}
              placeholder="Describe the lighting, atmosphere, or details you want…"
              rows={2}
              className="w-full resize-y rounded-lg border border-white/20 bg-white/5 px-3 py-2 text-xs text-white placeholder:text-white/40 focus:border-amber-400 focus:outline-none"
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
              disabled={isGenerating || needsCommunity3D}
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
              <button
                type="button"
                onClick={handleDownload}
                className="absolute top-3 right-14 rounded-full bg-black/60 p-2 text-white/80 hover:bg-black/80 hover:text-white transition"
                title="Download"
              >
                <Download size={20} />
              </button>
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
      {needsCommunity3D && (
        <div role="status" className="mb-2 flex flex-wrap items-center justify-center gap-2 rounded-lg bg-amber-50 px-4 py-3 text-center text-xs font-semibold text-amber-950 shadow-lg">
          <span>New or changed objects update automatically before a Direct 3D street render.</span>
          {onPrepareCommunity3D && <button type="button" onClick={onPrepareCommunity3D} className="rounded-full bg-[#c9ff3d] px-3 py-2 font-black text-[#151515]">Retry 3D update</button>}
        </div>
      )}
      {sourcePreview && sourcePreview.position === JSON.stringify(streetViewPegman.position) && sourcePreview.angle === streetViewPegman.angle && (
        <figure className="relative mx-auto mb-2 w-[min(100%,560px)] overflow-hidden rounded-lg bg-black shadow-xl">
          <img src={sourcePreview.imageUrl} alt="Street view 3D preview" className="max-h-[38vh] w-full object-contain" />
          <figcaption className="px-3 py-1 text-center text-xs text-white">Your 3D view · no AI render used</figcaption>
          <button type="button" aria-label="Close 3D preview" onClick={() => setSourcePreview(null)} className="absolute right-2 top-2 rounded bg-black/75 p-2 text-white"><X size={16} /></button>
        </figure>
      )}
      <div className="street-view-card street-view-card--panel flex max-h-[80dvh] flex-wrap items-center justify-center gap-3 overflow-y-auto rounded-lg px-4 py-3 backdrop-blur-xl">
        <div className="w-full">
          <label htmlFor="street-render-custom-prompt" className="mb-1 block text-xs font-bold">Custom prompt <span className="font-normal opacity-60">(optional)</span></label>
          <textarea
            spellCheck={true}
            lang="en-CA"
            id="street-render-custom-prompt"
            value={customPrompt}
            onChange={(event) => setCustomPrompt(event.target.value)}
            placeholder="Describe the lighting, atmosphere, or details you want…"
            rows={2}
            className="w-full resize-y rounded-lg border-2 border-[#151515]/20 bg-white/80 px-3 py-2 text-xs text-[#151515] placeholder:text-[#151515]/50 focus:border-[#151515] focus:outline-none"
          />
        </div>
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
          <RenderStyleGuideButton styles={STREET_VIEW_STYLES} selectedStyle={selectedStyle} onStyle={setSelectedStyle} disabled={isGenerating} className="mb-2" />
          {directStreetMode && <div className="mb-2"><ImageModelSelect value={imageModel} onChange={setImageModel} disabled={isGenerating} availability={imageModelAvailability} />{imageProgress && <p role="status" className="mt-1 text-xs">{imageProgress}</p>}</div>}
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

        {/* Real-world context toggle — colour inherits the always-cream card; an explicit
            text-[#151515] would get flipped to near-white by dark mode and vanish on the card. */}
        {!directStreetMode && <label className="flex max-w-[150px] cursor-pointer items-center gap-2 text-[10px] font-black uppercase leading-tight">
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
        </label>}

        {/* Direct 3D street: single inventory-locked call via the Direct 3D
            endpoint (review-first). Only meaningful on the globe mount. */}
        {globeCapture && (
          <button
            type="button"
            onClick={() => setDirectStreetMode((v) => !v)}
            title="One inventory-locked render through the selected GPT Image engine. Off = classic Gemini + GPT provider test."
            className={`rounded-full px-3 py-1.5 text-[10px] font-black uppercase leading-tight transition ${
              directStreetMode ? 'bg-[#c9ff3d] text-black' : 'bg-black/5 text-black/55 hover:bg-black/10'
            }`}
          >
            {directStreetMode ? `✓ Direct 3D · ${imageModel === 'compare-all-three' ? '3 images' : '1 image'}` : 'Classic comparison · 3 images'}
          </button>
        )}

        {/* Add people / vehicles toggles — default off for clean hero renders */}
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            onClick={() => setIncludePeople((v) => !v)}
            className={`rounded-full px-3 py-1.5 text-[10px] font-black uppercase leading-tight transition ${
              includePeople ? 'bg-[#c9ff3d] text-black' : 'bg-black/5 text-black/55 hover:bg-black/10'
            }`}
          >
            {includePeople ? '✓ People' : 'Add People'}
          </button>
          <button
            type="button"
            onClick={() => setIncludeVehicles((v) => !v)}
            className={`rounded-full px-3 py-1.5 text-[10px] font-black uppercase leading-tight transition ${
              includeVehicles ? 'bg-[#c9ff3d] text-black' : 'bg-black/5 text-black/55 hover:bg-black/10'
            }`}
          >
            {includeVehicles ? '✓ Vehicles' : 'Add Vehicles'}
          </button>
        </div>

        {/* Divider */}
        <div className="street-view-divider hidden h-16 w-px sm:block" />

        {/* Generate button */}
        {globeCapture && <button type="button" onClick={() => void previewStreetSource()} disabled={isGenerating || isPreviewing} className="rounded-full border-2 border-[#151515] px-3 py-2 text-xs font-bold disabled:opacity-50">
          {isPreviewing ? 'Preparing 3D view…' : 'Preview 3D view'}
        </button>}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || isPreviewing || needsCommunity3D || (directStreetMode && selectedEngineUnavailable)}
          className="street-view-generate-button flex min-h-12 items-center gap-2 rounded-full px-5 py-3 text-sm font-black uppercase transition disabled:opacity-50"
        >
          {isGenerating ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Rendering {directStreetMode ? imageProgress || 'Direct 3D Street' : STREET_VIEW_RENDER_LABEL}
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
