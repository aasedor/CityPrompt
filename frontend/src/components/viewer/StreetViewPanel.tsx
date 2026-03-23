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

      const res = await generateStreetView(
        streetViewPegman.position,
        streetViewPegman.angle,
        siteZones,
        {
          model: selectedModel !== 'gemini-2.5-flash-image' ? selectedModel : undefined,
          previousRenderBase64,
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
  }, [streetViewPegman, siteZones, generateStreetView, selectedModel, result]);

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
