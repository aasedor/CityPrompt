/**
 * GlobeAIRenderPanel.tsx — Simplified AI render controls for the 3D globe.
 *
 * Captures the globe canvas with photorealistic 3D tile context,
 * generates a mask from zone polygons, and sends to Gemini.
 */

import { useState, useCallback } from 'react';
import * as THREE from 'three';
import { Sparkles, Loader2, Download } from 'lucide-react';
import type { SiteZone } from '@/types';
import { useGlobeAIRender, type GlobeRenderResult, type GlobeRenderProgress, PERZONE_THRESHOLD } from './useGlobeAIRender';
import { rendersApi } from '@/services/api';

interface GlobeAIRenderPanelProps {
  canvas: HTMLCanvasElement | null;
  camera: THREE.Camera | null;
  siteZones: SiteZone[];
  terrainHeight: number;
  projectId?: string;
  onRenderComplete?: (result: GlobeRenderResult) => void;
}

const STYLES = [
  { id: 'photorealistic', label: 'Photo' },
  { id: 'photomontage', label: 'Montage' },
  { id: 'atmospheric', label: 'Dusk' },
  { id: 'spring', label: 'Spring' },
  { id: 'winter', label: 'Winter' },
  { id: 'night', label: 'Night' },
  { id: 'watercolour', label: 'Watercolour' },
  { id: 'charcoal', label: 'Charcoal' },
  { id: 'marker-render', label: 'Marker' },
  { id: 'clay-maquette', label: 'Clay' },
  { id: 'woodblock', label: 'Wood Block' },
  { id: 'collage', label: 'Collage' },
  { id: 'risograph', label: 'Risograph' },
  { id: 'pixel-art', label: 'Pixel Art' },
] as const;

export function GlobeAIRenderPanel({
  canvas,
  camera,
  siteZones,
  terrainHeight,
  projectId,
  onRenderComplete,
}: GlobeAIRenderPanelProps) {
  const { render, renderPerZone } = useGlobeAIRender();
  const [isRendering, setIsRendering] = useState(false);
  const [result, setResult] = useState<GlobeRenderResult | null>(null);
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');
  const [customPrompt, setCustomPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [renderTime, setRenderTime] = useState(0);
  const [renderProgress, setRenderProgress] = useState<GlobeRenderProgress | null>(null);

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
        console.log(`[GlobeAIRenderPanel] Using per-zone rendering (${editableZones.length} zones, mixed=${hasMixedTypes})`);
        renderResult = await renderPerZone(canvas, camera, siteZones, terrainHeight, {
          style: selectedStyle,
          projectId,
          customPrompt: customPrompt.trim() || undefined,
          onProgress: (progress) => setRenderProgress(progress),
        });
      } else {
        renderResult = await render(canvas, camera, editableZones, terrainHeight, {
          style: selectedStyle,
          projectId,
          customPrompt: customPrompt.trim() || undefined,
        });
      }

      if (renderResult) {
        setResult(renderResult);
        onRenderComplete?.(renderResult);
      } else {
        setError('Render returned no image. Try adjusting your view or zones.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Render failed. Please try again.');
    } finally {
      clearInterval(timer);
      setRenderTime(0);
      setRenderProgress(null);
      setIsRendering(false);
    }
  }, [canvas, camera, siteZones, terrainHeight, selectedStyle, isRendering, render, renderPerZone, projectId, onRenderComplete, customPrompt]);

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
    try {
      const base64 = result.imageUrl.split(',')[1];
      await rendersApi.save(projectId, {
        image_base64: base64,
        prompt: result.prompt,
        style: selectedStyle,
        seed: result.seed,
      });
    } finally {
      setSaving(false);
    }
  }, [result, projectId, selectedStyle, saving]);

  return (
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
              Generate Render
            </>
          )}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="px-4 pb-3">
          <div className="relative rounded-lg overflow-hidden border border-white/10">
            <img
              src={result.imageUrl}
              alt="AI Render"
              className="w-full cursor-pointer"
              onClick={handleDownload}
            />
            <div className="absolute bottom-0 left-0 right-0 flex justify-between items-center bg-gradient-to-t from-black/80 to-transparent px-2 py-1.5">
              <button
                onClick={handleSave}
                disabled={saving}
                className="text-[10px] text-white/80 hover:text-white"
              >
                {saving ? 'Saving...' : 'Save to Project'}
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
            onClick={() => setResult(null)}
            className="mt-1.5 w-full text-center text-[10px] text-gray-500 hover:text-gray-300"
          >
            Clear result
          </button>
        </div>
      )}
    </div>
  );
}
