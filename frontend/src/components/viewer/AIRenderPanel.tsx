/**
 * AIRenderPanel — UI panel for the aerial AI render pipeline.
 *
 * Provides a style picker, archetype toggle, advanced options disclosure,
 * preview card grid, and generate button with summary. Displays progress
 * and the result image with download/clear controls.
 */
import { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import type { Map as MapboxMap } from 'mapbox-gl';
import type { SiteZone } from '@/types';
import { useAIRender, AI_RENDER_STYLES } from './useAIRender';
import type { AIRenderResult } from './useAIRender';
import { collectArchetypeRenderInputs, mergeArchetypePrompts } from './collectArchetypeRenderInputs';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface AIRenderPanelProps {
  /** Ref to the live Mapbox map instance */
  mapRef: React.RefObject<MapboxMap | null>;
  /** Called when a render completes so the parent can overlay it on the map */
  onRenderComplete?: (result: AIRenderResult) => void;
  /** Called when previews are generated — parent can open a full-screen modal */
  onPreviewsReady?: (previews: AIRenderResult[]) => void;
  /** Called when the user clears the overlay */
  onClearOverlay?: () => void;
  /** Site zones — used to extract archetype prompt data */
  siteZones?: SiteZone[];
  /** Called when the user changes the render style — lets the parent sync style to other panels */
  onStyleChange?: (styleId: string) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AIRenderPanel({ mapRef, onRenderComplete, onPreviewsReady, onClearOverlay, siteZones = [], onStyleChange }: AIRenderPanelProps) {
  const {
    render,
    renderPerZone,
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
    statusMessage,
  } = useAIRender();

  // Local form state
  const [selectedStyle, setSelectedStyle] = useState(AI_RENDER_STYLES[0].id);
  const [customPrompt, setCustomPrompt] = useState('');
  const [controlStrength, setControlStrength] = useState(0.85);
  const [referenceImage, setReferenceImage] = useState<string | null>(null);
  const [referenceStrength, setReferenceStrength] = useState(0.6);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [useArchetypes, setUseArchetypes] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [guidanceScale, setGuidanceScale] = useState(15);
  const [perZoneMode, setPerZoneMode] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Hide zone polygon layers when a render result is displayed, restore when cleared
  const ZONE_LAYERS = [
    'site-zones-boundary-fill', 'site-zones-fill', 'site-zones-extrusion',
    'site-zones-outline', 'site-zones-selected', 'site-zones-labels',
  ];
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const visibility = result ? 'none' : 'visible';
    for (const layerId of ZONE_LAYERS) {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, 'visibility', visibility);
      }
    }
    // Restore layers on unmount
    return () => {
      for (const layerId of ZONE_LAYERS) {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, 'visibility', 'visible');
        }
      }
    };
  }, [result, mapRef]);

  // Extract archetype data from zone properties
  const archetypeInputs = useMemo(
    () => collectArchetypeRenderInputs(siteZones),
    [siteZones],
  );
  const hasArchetypes = archetypeInputs.positivePrompts.length > 0;

  const activeStyleLabel = useMemo(
    () => AI_RENDER_STYLES.find((s) => s.id === selectedStyle)?.label ?? selectedStyle,
    [selectedStyle],
  );

  // Handle reference image upload -> data-URI
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setReferenceImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  /** Build the shared render options from current form state */
  const buildRenderOptions = useCallback(() => {
    const archetype = useArchetypes && hasArchetypes
      ? mergeArchetypePrompts(archetypeInputs)
      : { archetypePrompt: undefined, archetypeNegative: undefined };

    // Find the site boundary zone to pass for masking
    const siteBoundary = siteZones.find((z) => z.zone_type === 'site_boundary');
    const siteBoundaryCoords = siteBoundary?.coordinates?.length
      ? siteBoundary.coordinates
      : undefined;

    return {
      style: selectedStyle,
      customPrompt: customPrompt.trim() || undefined,
      controlStrength,
      guidanceScale,
      referenceImageUrl: referenceImage || undefined,
      referenceStrength,
      archetypePrompt: archetype.archetypePrompt || undefined,
      archetypeNegative: archetype.archetypeNegative || undefined,
      referenceImageUrls: useArchetypes ? archetypeInputs.referenceImageUrls : undefined,
      // Pass enriched archetype render prompts — these replace the generic style preset when present
      mapOverlayPrompt: useArchetypes ? archetypeInputs.renderPrompt?.mapOverlay ?? undefined : undefined,
      mapOverlayNegative: useArchetypes ? archetypeInputs.renderPrompt?.negative ?? undefined : undefined,
      // Site boundary for compositing — render only changes pixels inside this polygon
      siteBoundaryCoords,
      // Pass all zones for inpainting mask generation
      siteZones: siteZones.length > 0 ? siteZones : undefined,
    };
  }, [selectedStyle, customPrompt, controlStrength, guidanceScale, referenceImage, referenceStrength, useArchetypes, hasArchetypes, archetypeInputs, siteZones]);

  /** Generate 3 preview renders in parallel */
  const handleGeneratePreviews = useCallback(async () => {
    const map = mapRef.current;
    if (!map) return;
    const results = await renderPreviews(map, buildRenderOptions());
    if (results.length > 0) {
      onPreviewsReady?.(results);
    }
  }, [mapRef, renderPreviews, buildRenderOptions, onPreviewsReady]);

  /** Select a preview and trigger full-quality render with its seed */
  const handleSelectPreview = useCallback(async (index: number) => {
    setSelectedPreviewIndex(index);
    const preview = previews[index];
    if (!preview?.seed) return;

    const map = mapRef.current;
    if (!map) return;

    const res = await renderFull(map, buildRenderOptions(), preview.seed);
    if (res) {
      onRenderComplete?.(res);
    }
  }, [previews, setSelectedPreviewIndex, mapRef, renderFull, buildRenderOptions, onRenderComplete]);

  /** Fallback: single render without previews */
  const handleRender = useCallback(async () => {
    const map = mapRef.current;
    if (!map) return;

    const opts = buildRenderOptions();
    const res = perZoneMode
      ? await renderPerZone(map, opts)
      : await render(map, opts);
    if (res) {
      onRenderComplete?.(res);
    }
  }, [mapRef, render, renderPerZone, perZoneMode, buildRenderOptions, onRenderComplete]);

  const handleClear = useCallback(() => {
    reset();
    onClearOverlay?.();
  }, [reset, onClearOverlay]);

  const handleDownload = useCallback(() => {
    if (!result?.imageUrl) return;
    const a = document.createElement('a');
    a.href = result.imageUrl;
    a.download = `ai-render-${Date.now()}.png`;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [result]);

  // Build summary text for generate button
  const summaryText = useMemo(() => {
    const parts: string[] = [activeStyleLabel];
    if (useArchetypes && hasArchetypes) {
      parts.push(`${archetypeInputs.positivePrompts.length} archetypes`);
    }
    return parts.join(' + ');
  }, [activeStyleLabel, useArchetypes, hasArchetypes, archetypeInputs]);

  // ── Minimal collapsed state ───────────────────────────────────────────
  if (isCollapsed) {
    return (
      <div className="absolute right-4 top-4 z-50">
        <button
          onClick={() => setIsCollapsed(false)}
          className="flex items-center gap-2 rounded-lg bg-gray-900/90 px-3 py-2 text-sm font-medium text-white shadow-lg backdrop-blur-sm transition hover:bg-gray-800/90"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          AI Render
          {result && <span className="h-2 w-2 rounded-full bg-green-400" />}
        </button>
      </div>
    );
  }

  // ── Full panel ────────────────────────────────────────────────────────
  return (
    <div className="absolute right-4 top-4 z-50 w-80 rounded-xl bg-gray-900/95 shadow-2xl backdrop-blur-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div className="flex items-center gap-2">
          <svg className="h-4 w-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          <span className="text-sm font-semibold text-white">AI Render</span>
        </div>
        <button
          onClick={() => setIsCollapsed(true)}
          className="rounded p-1 text-gray-400 transition hover:bg-white/10 hover:text-white"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12h-15" />
          </svg>
        </button>
      </div>

      <div className="max-h-[70vh] overflow-y-auto px-4 py-3 space-y-3">
        {/* ── Style picker ─────────────────────────────────────────────── */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-400">Style</label>
          <div className="grid grid-cols-3 gap-1">
            {AI_RENDER_STYLES.map((style) => (
              <button
                key={style.id}
                onClick={() => { setSelectedStyle(style.id); onStyleChange?.(style.id); }}
                className={`rounded-lg px-2 py-1.5 text-[11px] font-medium transition ${
                  selectedStyle === style.id
                    ? 'bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/50'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-gray-300'
                }`}
              >
                {style.label}
              </button>
            ))}
          </div>
        </div>

        {/* ── Archetype toggle ─────────────────────────────────────────── */}
        {hasArchetypes && (
          <div className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
            <div>
              <span className="text-xs font-medium text-gray-300">Archetype Styles</span>
              <p className="mt-0.5 text-[10px] text-gray-500">
                {archetypeInputs.positivePrompts.length} prompt{archetypeInputs.positivePrompts.length !== 1 ? 's' : ''}, {archetypeInputs.referenceImageUrls.length} ref{archetypeInputs.referenceImageUrls.length !== 1 ? 's' : ''}
              </p>
            </div>
            <button
              onClick={() => setUseArchetypes((v) => !v)}
              className={`relative h-5 w-9 rounded-full transition ${
                useArchetypes ? 'bg-amber-500' : 'bg-white/15'
              }`}
            >
              <span
                className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${
                  useArchetypes ? 'translate-x-4' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>
        )}

        {/* ── Advanced options disclosure ───────────────────────────────── */}
        <button
          onClick={() => setShowAdvanced((v) => !v)}
          className="flex w-full items-center gap-1.5 text-[11px] font-medium text-gray-500 transition hover:text-gray-300"
        >
          <svg
            className={`h-3 w-3 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
          Advanced Options
          {(customPrompt || referenceImage) && (
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
          )}
        </button>

        {showAdvanced && (
          <div className="space-y-3 rounded-lg border border-white/5 bg-white/[0.02] p-3">
            {/* Custom prompt */}
            <div>
              <label className="mb-1 block text-[11px] font-medium text-gray-400">
                Custom Prompt
              </label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="e.g. rainy evening, reflective puddles, warm streetlights..."
                rows={2}
                className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none focus:ring-1 focus:ring-amber-500/30"
              />
            </div>

            {/* Geometry fidelity */}
            <div>
              <div className="mb-1 flex items-center justify-between">
                <label className="text-[11px] font-medium text-gray-400">Geometry Fidelity</label>
                <span className="text-[10px] tabular-nums text-gray-500">{controlStrength.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0.3}
                max={1.0}
                step={0.05}
                value={controlStrength}
                onChange={(e) => setControlStrength(parseFloat(e.target.value))}
                className="w-full accent-amber-500"
              />
              <div className="mt-0.5 flex justify-between text-[9px] text-gray-600">
                <span>Creative</span>
                <span>Faithful</span>
              </div>
            </div>

            {/* Prompt Adherence */}
            <div>
              <div className="mb-1 flex items-center justify-between">
                <label className="text-[11px] font-medium text-gray-400">Prompt Adherence</label>
                <span className="text-[10px] tabular-nums text-gray-500">{guidanceScale}</span>
              </div>
              <input
                type="range"
                min={5}
                max={25}
                step={1}
                value={guidanceScale}
                onChange={(e) => setGuidanceScale(parseInt(e.target.value))}
                className="w-full accent-amber-500"
              />
              <div className="mt-0.5 flex justify-between text-[9px] text-gray-600">
                <span>Creative</span>
                <span>Strict</span>
              </div>
            </div>

            {/* Per-zone rendering toggle */}
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[11px] font-medium text-gray-400">Per-Zone Rendering</span>
                <p className="text-[9px] text-gray-600">Slower, higher detail per zone</p>
              </div>
              <button
                onClick={() => setPerZoneMode(!perZoneMode)}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${perZoneMode ? 'bg-amber-500' : 'bg-gray-600'}`}
              >
                <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${perZoneMode ? 'translate-x-4' : 'translate-x-0.5'}`} />
              </button>
            </div>

            {/* Reference image */}
            <div>
              <label className="mb-1 block text-[11px] font-medium text-gray-400">
                Reference Image
              </label>
              {referenceImage ? (
                <div className="relative">
                  <img src={referenceImage} alt="Reference" className="h-16 w-full rounded-lg object-cover" />
                  <button
                    onClick={() => {
                      setReferenceImage(null);
                      if (fileInputRef.current) fileInputRef.current.value = '';
                    }}
                    className="absolute right-1 top-1 rounded-full bg-black/60 p-0.5 text-white transition hover:bg-black/80"
                  >
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <div className="mt-1.5 flex items-center justify-between">
                    <label className="text-[10px] text-gray-500">Influence</label>
                    <span className="text-[10px] tabular-nums text-gray-500">{referenceStrength.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min={0.1}
                    max={1.0}
                    step={0.05}
                    value={referenceStrength}
                    onChange={(e) => setReferenceStrength(parseFloat(e.target.value))}
                    className="w-full accent-amber-500"
                  />
                </div>
              ) : (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-white/15 bg-white/5 py-2 text-[11px] text-gray-400 transition hover:border-white/25 hover:text-gray-300"
                >
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
                  </svg>
                  Upload reference
                </button>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>
        )}

        {/* ── Error ──────────────────────────────────────────────────────── */}
        {error && (
          <div className="rounded-lg bg-red-500/10 px-3 py-2 text-xs text-red-400">
            {error}
          </div>
        )}

        {/* ── Progress ──────────────────────────────────────────────────── */}
        {isRendering && (
          <div>
            <div className="mb-1 flex items-center justify-between">
              <span className="text-xs text-gray-400">{statusMessage || 'Generating render... Please wait'}</span>
              {progress > 0 && (
                <span className="text-xs tabular-nums text-gray-500">{progress}%</span>
              )}
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
              {progress <= 0 ? (
                <div className="h-full w-1/3 animate-pulse rounded-full bg-amber-500" />
              ) : (
                <div
                  className="h-full rounded-full bg-amber-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              )}
            </div>
          </div>
        )}

        {/* ── Preview cards ─────────────────────────────────────────────── */}
        {previews.length > 0 && !isRendering && (
          <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-400">
              Select a preview
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {previews.map((preview, idx) => (
                <button
                  key={preview.seed ?? idx}
                  onClick={() => handleSelectPreview(idx)}
                  className={`relative overflow-hidden rounded-lg border-2 transition ${
                    selectedPreviewIndex === idx
                      ? 'border-amber-400 shadow-lg shadow-amber-500/20'
                      : 'border-transparent hover:border-white/20'
                  }`}
                >
                  <img
                    src={preview.imageUrl}
                    alt={`Preview ${idx + 1}`}
                    className="aspect-square w-full object-cover"
                  />
                  {selectedPreviewIndex === idx && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                      <svg className="h-5 w-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                      </svg>
                    </div>
                  )}
                  <span className="absolute bottom-0.5 right-1 text-[9px] text-white/60">
                    #{idx + 1}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── Full result ───────────────────────────────────────────────── */}
        {result && !isRendering && (
          <div>
            <div className="mb-1.5 flex items-center justify-between">
              <span className="text-xs font-medium text-green-400">
                {selectedPreviewIndex != null ? 'Full quality render' : 'Render complete'}
              </span>
              <div className="flex gap-1">
                <button
                  onClick={handleDownload}
                  className="rounded px-2 py-1 text-[10px] font-medium text-gray-300 transition hover:bg-white/10"
                  title="Download render"
                >
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                </button>
                <button
                  onClick={handleClear}
                  className="rounded px-2 py-1 text-[10px] font-medium text-gray-300 transition hover:bg-white/10"
                  title="Clear overlay"
                >
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <img
              src={result.imageUrl}
              alt="AI Render"
              className="w-full rounded-lg shadow-md"
            />
          </div>
        )}

        {/* ── Generate buttons with summary ─────────────────────────────── */}
        <div className="flex gap-2">
          <button
            onClick={handleGeneratePreviews}
            disabled={isRendering}
            className={`flex flex-1 flex-col items-center justify-center gap-0.5 rounded-lg py-2.5 transition ${
              isRendering
                ? 'cursor-not-allowed bg-gray-700 text-gray-400'
                : 'bg-amber-500 text-black shadow-lg shadow-amber-500/25 hover:bg-amber-400'
            }`}
          >
            {isRendering ? (
              <span className="flex items-center gap-2 text-sm font-semibold">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
                  <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" className="opacity-75" />
                </svg>
                Rendering...
              </span>
            ) : (
              <>
                <span className="text-sm font-semibold">Generate Previews</span>
                <span className="text-[10px] font-normal opacity-70">{summaryText}</span>
              </>
            )}
          </button>
          {/* Quick single render */}
          {!isRendering && (
            <button
              onClick={handleRender}
              className="rounded-lg bg-white/10 px-3 py-2.5 text-xs font-medium text-gray-300 transition hover:bg-white/15"
              title="Single render (skip previews)"
            >
              1x
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
