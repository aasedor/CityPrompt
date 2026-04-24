/**
 * GlobeAIRenderPanel.tsx — Simplified AI render controls for the 3D globe.
 *
 * Captures the globe canvas with photorealistic 3D tile context,
 * generates a mask from zone polygons, and sends to Gemini.
 */

import { useState, useCallback, useEffect } from 'react';
import * as THREE from 'three';
import { Sparkles, Loader2, Download, X, Check, Image as ImageIcon } from 'lucide-react';
import type { SiteZone, SavedRender } from '@/types';
import { useGlobeAIRender, type GlobeRenderResult, type GlobeRenderProgress, PERZONE_THRESHOLD } from './useGlobeAIRender';
import { rendersApi, resolveApiFileUrl } from '@/services/api';

const PREVIEW_COUNT = 3;

interface GlobeAIRenderPanelProps {
  canvas: HTMLCanvasElement | null;
  camera: THREE.Camera | null;
  siteZones: SiteZone[];
  terrainHeight: number;
  projectId?: string;
  onRenderComplete?: (result: GlobeRenderResult) => void;
}

const STYLES = [
  // Photo family
  { id: 'photorealistic', label: 'Photo Realistic' },
  { id: 'photomontage', label: 'Photomontage' },
  { id: 'atmospheric', label: 'Atmospheric' },
  // Site plan family (ported from codex — near-top-down styles)
  { id: 'site-plan', label: 'Site Plan' },
  { id: 'site-plan-photo', label: 'Site Plan Photo' },
  { id: 'site-plan-watercolor', label: 'Site Plan WC' },
  // Seasonal
  { id: 'spring', label: 'Spring' },
  { id: 'winter', label: 'Winter' },
  { id: 'night', label: 'Night' },
  // Artistic
  { id: 'watercolour', label: 'Watercolour' },
  { id: 'charcoal', label: 'Charcoal' },
  { id: 'isometric', label: 'Isometric' },
  { id: 'woodblock', label: 'Wood Block' },
  { id: 'marker-render', label: 'Marker' },
  { id: 'clay-maquette', label: 'Clay' },
  // Experimental
  { id: 'collage', label: 'Collage' },
  { id: 'risograph', label: 'Risograph' },
  { id: 'pixel-art', label: 'Pixel Art' },
] as const;

type LightboxRender = {
  imageUrl: string;
  prompt?: string;
  style?: string;
  createdAt?: string;
  downloadName: string;
};

export function GlobeAIRenderPanel({
  canvas,
  camera,
  siteZones,
  terrainHeight,
  projectId,
  onRenderComplete,
}: GlobeAIRenderPanelProps) {
  const { render, renderPreviews, renderPerZone } = useGlobeAIRender();
  const [isRendering, setIsRendering] = useState(false);
  const [result, setResult] = useState<GlobeRenderResult | null>(null);
  const [previews, setPreviews] = useState<GlobeRenderResult[]>([]);
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number | null>(null);
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');
  const [customPrompt, setCustomPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved' | 'error'>('idle');
  const [savedRenders, setSavedRenders] = useState<SavedRender[]>([]);
  const [showSavedRenders, setShowSavedRenders] = useState(false);
  const [renderTime, setRenderTime] = useState(0);
  const [renderProgress, setRenderProgress] = useState<GlobeRenderProgress | null>(null);
  // Lightbox: render currently shown full-screen (null = closed).
  const [lightboxRender, setLightboxRender] = useState<LightboxRender | null>(null);

  const refreshSavedRenders = useCallback(async () => {
    if (!projectId) {
      setSavedRenders([]);
      return;
    }
    try {
      setSavedRenders(await rendersApi.list(projectId));
    } catch {
      // The gallery is supplemental; render controls should stay usable.
    }
  }, [projectId]);

  useEffect(() => {
    refreshSavedRenders();
  }, [refreshSavedRenders]);

  useEffect(() => {
    setSaveStatus('idle');
  }, [result?.imageUrl]);

  const handleRender = useCallback(async () => {
    if (!canvas || !camera || isRendering) return;

    const editableZones = siteZones.filter(z =>
      z.zone_type !== 'site_boundary' && z.coordinates.length >= 3
    );

    if (editableZones.length === 0) {
      setError('Draw some zones first before rendering');
      return;
    }

    setIsRendering(true);
    setResult(null);
    setPreviews([]);
    setSelectedPreviewIndex(null);
    setError(null);
    setRenderProgress(null);
    const startTime = Date.now();
    const timer = setInterval(() => setRenderTime(Math.round((Date.now() - startTime) / 1000)), 1000);

    try {
      // Use per-zone when: 5+ zones, OR mixing roads/streets with buildings
      // (roads and buildings have such different archetypes that single-shot confuses Gemini)
      const ROAD_TYPES = ['road', 'street', 'path'];
      const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
      const hasRoads = editableZones.some(z => ROAD_TYPES.includes(z.zone_type));
      const hasBuildings = editableZones.some(z => BUILDING_TYPES.includes(z.zone_type));
      const hasMixedTypes = hasRoads && hasBuildings;
      const usePerZone = editableZones.length >= PERZONE_THRESHOLD; // Single-shot is default — per-zone only for 5+ zones
      let renderResult: GlobeRenderResult | null;

      if (usePerZone) {
        // Per-zone path is already sequential and slow — don't fan out previews.
        console.log(`[GlobeAIRenderPanel] Using per-zone rendering (${editableZones.length} zones, mixed=${hasMixedTypes})`);
        renderResult = await renderPerZone(canvas, camera, siteZones, terrainHeight, {
          style: selectedStyle,
          projectId,
          customPrompt: customPrompt.trim() || undefined,
          onProgress: (progress) => setRenderProgress(progress),
        });
        if (renderResult) {
          setResult(renderResult);
          onRenderComplete?.(renderResult);
        } else {
          setError('Render returned no image. Try adjusting your view or zones.');
        }
      } else {
        // Single-shot: fan out N parallel previews with different server seeds.
        // First preview is auto-selected so the user sees a large image
        // immediately; clicking a thumbnail switches the selection.
        const results = await renderPreviews(canvas, camera, editableZones, terrainHeight, {
          style: selectedStyle,
          projectId,
          customPrompt: customPrompt.trim() || undefined,
          count: PREVIEW_COUNT,
        });
        if (results.length > 0) {
          setPreviews(results);
          setSelectedPreviewIndex(0);
          setResult(results[0]);
          onRenderComplete?.(results[0]);
        } else {
          setError('Render returned no image. Try adjusting your view or zones.');
        }
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Render failed. Please try again.');
    } finally {
      clearInterval(timer);
      setRenderTime(0);
      setRenderProgress(null);
      setIsRendering(false);
    }
  }, [canvas, camera, siteZones, terrainHeight, selectedStyle, isRendering, render, renderPreviews, renderPerZone, projectId, onRenderComplete, customPrompt]);

  // Close lightbox on Esc
  useEffect(() => {
    if (!lightboxRender) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setLightboxRender(null); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [lightboxRender]);

  const handleSelectPreview = useCallback((index: number) => {
    if (index < 0 || index >= previews.length) return;
    setSelectedPreviewIndex(index);
    setResult(previews[index]);
    onRenderComplete?.(previews[index]);
  }, [previews, onRenderComplete]);

  const handleDownload = useCallback(() => {
    if (!result?.imageUrl) return;
    const a = document.createElement('a');
    a.href = result.imageUrl;
    a.download = `siteforge-globe-render-${Date.now()}.png`;
    a.click();
  }, [result]);

  const handleSave = useCallback(async () => {
    if (!result?.imageUrl || !projectId || saving) return;
    setSaving(true);
    setSaveStatus('idle');
    try {
      let base64 = '';
      if (result.imageUrl.startsWith('data:')) {
        base64 = result.imageUrl.split(',')[1] || '';
      } else {
        const resp = await fetch(result.imageUrl);
        const blob = await resp.blob();
        base64 = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve((reader.result as string).split(',')[1] || '');
          reader.readAsDataURL(blob);
        });
      }
      const saved = await rendersApi.save(projectId, {
        image_base64: base64,
        prompt: result.prompt,
        style: selectedStyle,
        seed: result.seed,
      });
      setSavedRenders((prev) => [saved, ...prev.filter((r) => r.id !== saved.id)]);
      setShowSavedRenders(true);
      setSaveStatus('saved');
    } catch {
      setSaveStatus('error');
    } finally {
      setSaving(false);
    }
  }, [result, projectId, selectedStyle, saving]);

  const openResultLightbox = useCallback((renderResult: GlobeRenderResult, label: string) => {
    setLightboxRender({
      imageUrl: renderResult.imageUrl,
      prompt: renderResult.prompt,
      style: selectedStyle,
      downloadName: `${label}-${Date.now()}.png`,
    });
  }, [selectedStyle]);

  return (
    <>
    <div className="w-full rounded-xl bg-gray-900/95 backdrop-blur-sm shadow-2xl border border-white/10">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/10">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Sparkles size={14} className="text-amber-400" />
          AI Render (Globe)
        </h3>
        <p className="mt-0.5 text-[10px] text-gray-400">
          Renders use photorealistic 3D context from Google Earth tiles
        </p>
      </div>

      {/* Style selector */}
      <div className="px-4 py-2 border-b border-white/10">
        <div className="flex flex-wrap gap-1.5">
          {STYLES.map(s => (
            <button
              key={s.id}
              onClick={() => setSelectedStyle(s.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                selectedStyle === s.id
                  ? 'bg-amber-500 text-black'
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom prompt */}
      <div className="px-4 py-2 border-b border-white/10">
        <textarea
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          placeholder="Additional instructions (optional)..."
          rows={2}
          className="w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-xs text-white placeholder-gray-500 resize-none focus:outline-none focus:border-amber-500/50"
        />
      </div>

      {/* Error display */}
      {error && (
        <div className="px-4 py-2">
          <div className="rounded-lg bg-red-500/20 border border-red-500/30 px-3 py-2 text-xs text-red-300">
            {error}
          </div>
        </div>
      )}

      {/* Render button */}
      <div className="px-4 py-3">
        <button
          onClick={handleRender}
          disabled={isRendering || !canvas || !camera}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg transition hover:from-amber-400 hover:to-orange-400 disabled:opacity-50"
        >
          {isRendering ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              {renderProgress
                ? `Rendering ${renderProgress.step}/${renderProgress.total}: ${renderProgress.zoneName}... ${renderTime > 0 ? `(${renderTime}s)` : ''}`
                : `Rendering... ${renderTime > 0 ? `(${renderTime}s)` : ''}`
              }
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Generate Previews
            </>
          )}
        </button>
      </div>

      {/* Preview grid (only when multiple previews exist) */}
      {previews.length > 1 && (
        <div className="px-4 pb-2">
          <div className="mb-1 flex items-center justify-between text-[10px] text-gray-400">
            <span>Variant {selectedPreviewIndex !== null ? selectedPreviewIndex + 1 : '?'} of {previews.length}</span>
            <span>open any preview</span>
          </div>
          <div className="grid grid-cols-3 gap-1.5">
            {previews.map((p, i) => (
              <button
                key={i}
                onClick={() => {
                  handleSelectPreview(i);
                  openResultLightbox(p, `siteforge-globe-preview-${i + 1}`);
                }}
                className={`relative aspect-square overflow-hidden rounded border-2 transition ${
                  selectedPreviewIndex === i
                    ? 'border-amber-400 ring-2 ring-amber-400/40'
                    : 'border-white/10 hover:border-white/40'
                }`}
                title={`Preview ${i + 1}${p.seed !== undefined ? ` (seed ${p.seed})` : ''} - open larger`}
              >
                <img
                  src={p.imageUrl}
                  alt={`Preview ${i + 1}`}
                  className="h-full w-full object-cover"
                />
                <span className="pointer-events-none absolute left-1 top-1 rounded bg-black/60 px-1 text-[10px] font-bold text-white">
                  {i + 1}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="px-4 pb-3">
          <div className="relative rounded-lg overflow-hidden border border-white/10">
            <img
              src={result.imageUrl}
              alt="AI Render"
              className="w-full cursor-zoom-in"
              onClick={() => openResultLightbox(result, 'siteforge-globe-render')}
              title="Click to enlarge"
            />
            <div className="absolute bottom-0 left-0 right-0 flex justify-between items-center bg-gradient-to-t from-black/80 to-transparent px-2 py-1.5">
              <button
                onClick={handleSave}
                disabled={saving || saveStatus === 'saved'}
                className="flex items-center gap-1 text-[10px] text-white/80 hover:text-white disabled:opacity-70"
              >
                {saving && <Loader2 size={10} className="animate-spin" />}
                {saveStatus === 'saved' && <Check size={10} />}
                {saving ? 'Saving...' : saveStatus === 'saved' ? 'Saved' : saveStatus === 'error' ? 'Retry save' : 'Save to Project'}
              </button>
              <button
                onClick={handleDownload}
                className="text-[10px] text-white/80 hover:text-white flex items-center gap-1"
              >
                <Download size={10} />
                Download
              </button>
            </div>
          </div>
          <button
            onClick={() => {
              setResult(null);
              setPreviews([]);
              setSelectedPreviewIndex(null);
            }}
            className="mt-1.5 w-full text-center text-[10px] text-gray-500 hover:text-gray-300"
          >
            Clear result
          </button>
        </div>
      )}

      {/* Saved renders gallery */}
      {projectId && (
        <div className="border-t border-white/10 px-4 py-3">
          <button
            onClick={() => setShowSavedRenders((v) => !v)}
            className="flex w-full items-center justify-between text-xs font-medium text-gray-400 transition hover:text-gray-200"
          >
            <span className="flex items-center gap-1.5">
              <ImageIcon size={13} />
              Saved Renders
            </span>
            <span>{savedRenders.length}</span>
          </button>

          {showSavedRenders && (
            <div className="mt-3">
              {savedRenders.length === 0 ? (
                <p className="py-3 text-center text-xs text-gray-500">
                  Save a render to keep it with this project.
                </p>
              ) : (
                <div className="grid grid-cols-3 gap-2">
                  {savedRenders.map((saved) => {
                    const savedUrl = resolveApiFileUrl(saved.image_url);
                    return (
                      <button
                        key={saved.id}
                        onClick={() => setLightboxRender({
                          imageUrl: savedUrl,
                          prompt: saved.prompt,
                          style: saved.style,
                          createdAt: saved.created_at,
                          downloadName: `render-${saved.id}.png`,
                        })}
                        className="group relative aspect-square overflow-hidden rounded border border-white/10 transition hover:border-amber-400/60"
                        title="Open saved render"
                      >
                        <img
                          src={savedUrl}
                          alt={saved.prompt || 'Saved render'}
                          className="h-full w-full object-cover"
                        />
                        <span className="absolute inset-x-0 bottom-0 truncate bg-black/65 px-1 py-0.5 text-left text-[9px] text-white/80 opacity-0 transition group-hover:opacity-100">
                          {saved.style || new Date(saved.created_at).toLocaleDateString()}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>

    {/* Lightbox overlay — click ANYWHERE (including the image), press Esc, or
        click the explicit ✕ button to close. Rendered at the root so it
        overlays the whole viewport regardless of where the panel is mounted. */}
    {lightboxRender && (
      <div
        className="fixed inset-0 z-[100] flex cursor-zoom-out items-center justify-center bg-black/90 p-6"
        onClick={() => setLightboxRender(null)}
        role="dialog"
        aria-label="Render preview — click anywhere or press Esc to close"
      >
        {/* Explicit, high-contrast close button — always reachable. */}
        <a
          href={lightboxRender.imageUrl}
          download={lightboxRender.downloadName}
          onClick={(e) => e.stopPropagation()}
          className="absolute top-4 right-16 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black text-white shadow-lg ring-2 ring-white/30 transition hover:bg-white hover:text-black"
          aria-label="Download render"
          title="Download"
        >
          <Download size={20} />
        </a>
        <button
          onClick={(e) => { e.stopPropagation(); setLightboxRender(null); }}
          className="absolute top-4 right-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black text-white shadow-lg ring-2 ring-white/30 transition hover:bg-white hover:text-black"
          aria-label="Close"
          title="Close (Esc)"
        >
          <X size={22} />
        </button>
        <div className="flex max-h-full max-w-full flex-col items-center gap-3" onClick={(e) => e.stopPropagation()}>
          <img
            src={lightboxRender.imageUrl}
            alt="Enlarged render"
            className="max-h-[82vh] max-w-[92vw] rounded-lg object-contain shadow-2xl"
          />
          {(lightboxRender.prompt || lightboxRender.style || lightboxRender.createdAt) && (
            <div className="max-w-3xl rounded-lg bg-black/60 px-4 py-2 text-center text-xs text-white/75">
              {lightboxRender.prompt && <p className="line-clamp-2">{lightboxRender.prompt}</p>}
              {(lightboxRender.style || lightboxRender.createdAt) && (
                <p className="mt-1 text-white/45">
                  {[lightboxRender.style, lightboxRender.createdAt ? new Date(lightboxRender.createdAt).toLocaleDateString() : null]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    )}
    </>
  );
}
