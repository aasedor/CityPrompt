import { useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { Loader2, LayoutGrid, RefreshCw, Check, Lock, Unlock, ImageIcon } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZone, LayoutOption, OSMContext, LockedLayers } from '@/types';
import { siteZonesApi } from '@/services/api';
import { useViewerStore } from '@/store';
import { SitePlanDiagram } from './SitePlanDiagram';

interface LayoutPreviewPanelProps {
  zone: SiteZone;
  onApplied: () => void;
  onAIGenerate?: (buildingId: string, initialPrompt?: string) => void;
  referenceContext?: OSMContext | null;
  siblingZones?: SiteZone[];
}

export function LayoutPreviewPanel({ zone, onApplied, referenceContext, siblingZones }: LayoutPreviewPanelProps) {
  const navigate = useNavigate();
  const {
    layoutPreview, setLayoutPreview, clearLayoutPreview, setActivePreviewIndex,
    setPreviewImageUrl, setLightboxImage,
    lockedLayers, toggleLayerLock, clearLockedLayers,
  } = useViewerStore();
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [renderingIndices, setRenderingIndices] = useState<Set<number>>(new Set());
  const [failedIndices, setFailedIndices] = useState<Set<number>>(new Set());
  const autoRenderTriggered = useRef(false);

  const isPreviewActive = layoutPreview?.zoneId === zone.id;
  const options = isPreviewActive ? layoutPreview!.options : [];
  const activeIndex = isPreviewActive ? layoutPreview!.activeIndex : 0;
  const activeOption = options[activeIndex];
  // Image URLs persisted in Zustand store (survives navigation)
  const previewImages = isPreviewActive ? layoutPreview!.imageUrls : {};

  // Auto-render AI previews for all options after layout generation
  useEffect(() => {
    if (!isPreviewActive || options.length === 0 || autoRenderTriggered.current) return;
    // Don't auto-render if we already have images for all options
    const allRendered = options.every((_, idx) => previewImages[idx]);
    if (allRendered) return;

    autoRenderTriggered.current = true;
    // Render only options that don't already have images
    options.forEach((opt, idx) => {
      if (previewImages[idx]) return; // Skip already rendered (persisted from previous visit)
      renderOption(idx, opt);
    });
  }, [isPreviewActive, options.length]); // eslint-disable-line react-hooks/exhaustive-deps

  // Reset auto-render flag when zone changes
  useEffect(() => {
    autoRenderTriggered.current = false;
    setFailedIndices(new Set());
  }, [zone.id]);

  const renderOption = async (idx: number, option: LayoutOption) => {
    setRenderingIndices((prev) => new Set(prev).add(idx));
    setFailedIndices((prev) => {
      const next = new Set(prev);
      next.delete(idx);
      return next;
    });
    try {
      const result = await siteZonesApi.renderLayoutPreview(zone.id, option);
      // Store image URL in Zustand store so it persists across navigation
      setPreviewImageUrl(idx, result.image_url);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || 'Unknown error';
      console.error(`Preview render failed for option ${idx}:`, detail, err);
      setFailedIndices((prev) => new Set(prev).add(idx));
      toast.error(`Preview ${idx + 1}: ${detail}`, { duration: 8000 });
    } finally {
      setRenderingIndices((prev) => {
        const next = new Set(prev);
        next.delete(idx);
        return next;
      });
    }
  };

  const handlePreview = async () => {
    setLoading(true);
    autoRenderTriggered.current = false;
    setFailedIndices(new Set());
    try {
      const response = await siteZonesApi.previewLayouts(zone.id);
      setLayoutPreview(zone.id, response.options); // Resets imageUrls to {}
      clearLockedLayers();
      toast.success(`Generated ${response.options.length} layout options — rendering previews...`);
    } catch {
      toast.error('Failed to generate layout options');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!isPreviewActive || !options[activeIndex]) return;
    setApplying(true);
    try {
      const chosen = options[activeIndex];
      await siteZonesApi.applyLayout(zone.id, chosen.option_index, chosen);
      clearLayoutPreview();
      clearLockedLayers();
      toast.success('Layout applied — buildings created');
      onApplied();
    } catch {
      toast.error('Failed to apply layout');
    } finally {
      setApplying(false);
    }
  };

  const handleRegenerate = async () => {
    if (!lockedLayers) return;
    setRegenerating(true);
    autoRenderTriggered.current = false;
    setFailedIndices(new Set());
    try {
      const response = await siteZonesApi.regenerateLayout(zone.id, lockedLayers);
      setLayoutPreview(zone.id, response.options); // Resets imageUrls to {}
      toast.success(`Regenerated ${response.options.length} layout options — rendering previews...`);
    } catch {
      toast.error('Failed to regenerate layout');
    } finally {
      setRegenerating(false);
    }
  };

  const hasLockedAnything = lockedLayers && (
    lockedLayers.roads.length > 0 ||
    lockedLayers.buildings.length > 0 ||
    lockedLayers.green_spaces.length > 0
  );

  // Not yet previewing — show the trigger button
  if (!isPreviewActive) {
    return (
      <button
        onClick={handlePreview}
        disabled={loading}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-500 px-3 py-1.5 text-xs font-medium text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-400 disabled:opacity-50"
      >
        {loading ? <Loader2 size={12} className="animate-spin" /> : <LayoutGrid size={12} />}
        {loading ? 'Generating layout options...' : 'Preview Layouts'}
      </button>
    );
  }

  const renderingCount = renderingIndices.size;

  // Previewing — show option cards with AI-rendered images
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-primary-950/60 dark:text-white/60">Layout Options</span>
        <div className="flex items-center gap-2">
          {renderingCount > 0 && (
            <span className="flex items-center gap-1 text-[10px] text-purple-400">
              <Loader2 size={9} className="animate-spin" />
              Rendering {renderingCount}...
            </span>
          )}
          <button
            onClick={handlePreview}
            disabled={loading}
            className="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] text-indigo-400 hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.04]"
            title="Regenerate options"
          >
            <RefreshCw size={10} className={loading ? 'animate-spin' : ''} />
            Regenerate
          </button>
        </div>
      </div>

      {options.map((opt, idx) => (
        <OptionCard
          key={idx}
          option={opt}
          zone={zone}
          isActive={idx === activeIndex}
          onClick={() => setActivePreviewIndex(idx)}
          referenceContext={referenceContext}
          lockedLayers={lockedLayers}
          siblingZones={siblingZones}
          previewImageUrl={previewImages[idx]}
          isRendering={renderingIndices.has(idx)}
          hasFailed={failedIndices.has(idx)}
          onRerender={() => renderOption(idx, opt)}
          onImageClick={previewImages[idx] ? () => setLightboxImage(previewImages[idx]) : undefined}
        />
      ))}

      {/* Expanded view for active option */}
      {activeOption && (
        <div className="rounded-lg border border-indigo-400/20 bg-indigo-500/10 p-2">
          {previewImages[activeIndex] ? (
            <img
              src={previewImages[activeIndex]}
              alt="AI-rendered layout preview"
              className="w-full rounded cursor-zoom-in"
              onClick={() => setLightboxImage(previewImages[activeIndex])}
            />
          ) : renderingIndices.has(activeIndex) ? (
            <div className="flex h-[200px] items-center justify-center rounded bg-white dark:bg-primary-900">
              <div className="flex flex-col items-center gap-2">
                <Loader2 size={20} className="animate-spin text-purple-400" />
                <span className="text-[10px] text-primary-950/50 dark:text-white/50">Rendering realistic preview...</span>
              </div>
            </div>
          ) : failedIndices.has(activeIndex) ? (
            <div className="flex h-[200px] items-center justify-center rounded bg-red-50">
              <div className="flex flex-col items-center gap-2">
                <span className="text-[10px] text-red-600">Render failed</span>
                <button
                  onClick={() => renderOption(activeIndex, activeOption)}
                  className="flex items-center gap-1 rounded bg-primary-950/[0.04] dark:bg-white/[0.04] px-2 py-1 text-[10px] text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]"
                >
                  <RefreshCw size={9} />
                  Retry
                </button>
              </div>
            </div>
          ) : (
            <SitePlanDiagram
              zone={zone}
              option={activeOption}
              referenceContext={referenceContext}
              lockedLayers={lockedLayers}
              siblingZones={siblingZones}
              width={270}
              height={200}
              showLabels
              showDimensions
            />
          )}
        </div>
      )}

      {/* Layer Lock Controls */}
      {activeOption && (
        <div className="rounded-lg border border-primary-950/[0.08] dark:border-white/[0.08] bg-white dark:bg-primary-900 p-2 space-y-1.5">
          <span className="text-[10px] font-semibold text-primary-950/50 dark:text-white/50 uppercase tracking-wide">Lock Layers</span>
          <div className="flex gap-1.5">
            <LayerLockButton
              label="Roads"
              count={activeOption.roads.length}
              isLocked={lockedLayers?.roads.length === activeOption.roads.length && activeOption.roads.length > 0}
              onClick={() => {
                const indices = activeOption.roads.map((_, i) => i);
                toggleLayerLock('roads', indices);
              }}
            />
            <LayerLockButton
              label="Buildings"
              count={activeOption.buildings.length}
              isLocked={lockedLayers?.buildings.length === activeOption.buildings.length && activeOption.buildings.length > 0}
              onClick={() => {
                const indices = activeOption.buildings.map((_, i) => i);
                toggleLayerLock('buildings', indices);
              }}
            />
            <LayerLockButton
              label="Green"
              count={activeOption.green_spaces.length}
              isLocked={lockedLayers?.green_spaces.length === activeOption.green_spaces.length && activeOption.green_spaces.length > 0}
              onClick={() => {
                const indices = activeOption.green_spaces.map((_, i) => i);
                toggleLayerLock('green_spaces', indices);
              }}
            />
          </div>
          {hasLockedAnything && (
            <button
              onClick={handleRegenerate}
              disabled={regenerating}
              className="flex w-full items-center justify-center gap-1.5 rounded bg-amber-500 px-2 py-1 text-[10px] font-medium text-white shadow-lg shadow-amber-500/25 hover:bg-amber-400 disabled:opacity-50"
            >
              {regenerating ? <Loader2 size={10} className="animate-spin" /> : <RefreshCw size={10} />}
              {regenerating ? 'Regenerating...' : 'Regenerate Unlocked Layers'}
            </button>
          )}
        </div>
      )}

      <button
        onClick={() => navigate(`/projects/${zone.project_id}/block-editor/${zone.id}`)}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-500 px-3 py-2 text-xs font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-400"
      >
        <LayoutGrid size={12} />
        Edit & Finalize in Block Editor
      </button>

      <button
        onClick={handleApply}
        disabled={applying}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-green-600 px-3 py-2 text-xs font-semibold text-white shadow-lg shadow-green-600/25 hover:bg-green-500 disabled:opacity-50"
      >
        {applying ? <Loader2 size={12} className="animate-spin" /> : <Check size={12} />}
        {applying ? 'Applying...' : 'Apply This Layout'}
      </button>

      <button
        onClick={() => { clearLayoutPreview(); clearLockedLayers(); }}
        className="w-full rounded-lg border border-primary-950/[0.08] dark:border-white/[0.08] px-3 py-1.5 text-xs text-primary-950/50 dark:text-white/50 hover:bg-white"
      >
        Cancel Preview
      </button>
    </div>
  );
}

function OptionCard({
  option,
  zone,
  isActive,
  onClick,
  referenceContext,
  lockedLayers,
  siblingZones,
  previewImageUrl,
  isRendering,
  hasFailed,
  onRerender,
  onImageClick,
}: {
  option: LayoutOption;
  zone: SiteZone;
  isActive: boolean;
  onClick: () => void;
  referenceContext?: OSMContext | null;
  lockedLayers?: LockedLayers | null;
  siblingZones?: SiteZone[];
  previewImageUrl?: string;
  isRendering?: boolean;
  hasFailed?: boolean;
  onRerender?: () => void;
  onImageClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`w-full cursor-pointer rounded-lg border p-2 text-left transition-all ${
        isActive
          ? 'border-indigo-400/40 bg-indigo-500/15 ring-1 ring-indigo-400/30'
          : 'border-primary-950/[0.08] dark:border-white/[0.08] bg-white dark:bg-primary-900 hover:border-primary-950/[0.12] hover:bg-white'
      }`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className={`text-xs font-semibold ${isActive ? 'text-indigo-300' : 'text-primary-950/70 dark:text-white/70'}`}>
          {option.option_label}
        </span>
        <span className="text-[10px] text-primary-950/40 dark:text-white/40">
          {option.buildings.length} units
        </span>
      </div>

      {/* Primary: AI-rendered image. Fallback: SVG diagram while rendering */}
      {previewImageUrl ? (
        <div className="relative">
          <img
            src={previewImageUrl}
            alt="AI-rendered preview"
            className={`w-full rounded${onImageClick ? ' cursor-zoom-in' : ''}`}
            onClick={onImageClick ? (e) => { e.stopPropagation(); onImageClick(); } : undefined}
            onError={(e) => {
              console.error('Preview image failed to load:', previewImageUrl);
              (e.target as HTMLImageElement).style.display = 'none';
              const p = (e.target as HTMLImageElement).nextElementSibling as HTMLElement;
              if (p?.dataset.placeholder) p.style.display = 'flex';
            }}
          />
          <div data-placeholder="true" className="h-[140px] items-center justify-center rounded bg-red-50 text-[9px] text-red-600" style={{ display: 'none' }}>
            Image failed to load
          </div>
          {onRerender && (
            <button
              onClick={(e) => { e.stopPropagation(); onRerender(); }}
              className="absolute bottom-1 right-1 rounded bg-black/50 p-1 text-primary-950/80 dark:text-white/80 hover:bg-black/70 hover:text-primary-950 dark:hover:text-accent-50"
              title="Re-render preview"
            >
              <RefreshCw size={10} />
            </button>
          )}
        </div>
      ) : isRendering ? (
        <div className="flex h-[140px] items-center justify-center rounded bg-white dark:bg-primary-900">
          <div className="flex flex-col items-center gap-1.5">
            <Loader2 size={16} className="animate-spin text-purple-400" />
            <span className="text-[9px] text-primary-950/40 dark:text-white/40">Rendering...</span>
          </div>
        </div>
      ) : hasFailed ? (
        <div className="flex h-[140px] items-center justify-center rounded bg-red-50">
          <div className="flex flex-col items-center gap-1.5">
            <span className="text-[9px] text-red-600">Failed</span>
            {onRerender && (
              <button
                onClick={(e) => { e.stopPropagation(); onRerender(); }}
                className="flex items-center gap-1 rounded bg-primary-950/[0.04] dark:bg-white/[0.04] px-1.5 py-0.5 text-[9px] text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]"
              >
                <RefreshCw size={8} />
                Retry
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="relative">
          <SitePlanDiagram
            zone={zone}
            option={option}
            referenceContext={referenceContext}
            lockedLayers={isActive ? lockedLayers : undefined}
            siblingZones={siblingZones}
            width={250}
            height={140}
            showLabels={false}
            showDimensions={false}
          />
          {onRerender && (
            <button
              onClick={(e) => { e.stopPropagation(); onRerender(); }}
              className="absolute bottom-1 right-1 flex items-center gap-1 rounded bg-purple-500/80 px-1.5 py-0.5 text-[9px] font-medium text-primary-950 dark:text-accent-50 hover:bg-purple-500"
            >
              <ImageIcon size={9} />
              Render
            </button>
          )}
        </div>
      )}

      {option.density_achieved && (
        <div className="mt-1 text-[10px] text-primary-950/40 dark:text-white/40">
          {option.density_achieved} units/ha
        </div>
      )}
      <p className="mt-0.5 text-[10px] leading-tight text-primary-950/50 dark:text-white/50 line-clamp-2">
        {option.reasoning}
      </p>
    </div>
  );
}

function LayerLockButton({
  label,
  count,
  isLocked,
  onClick,
}: {
  label: string;
  count: number;
  isLocked: boolean;
  onClick: () => void;
}) {
  if (count === 0) return null;
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1 rounded px-2 py-1 text-[10px] font-medium transition-colors ${
        isLocked
          ? 'bg-amber-500/20 text-amber-400 border border-amber-400/30'
          : 'bg-white dark:bg-primary-900 text-primary-950/50 dark:text-white/50 border border-primary-950/[0.08] dark:border-white/[0.08] hover:bg-primary-950/[0.04] dark:hover:bg-white/[0.04]'
      }`}
    >
      {isLocked ? <Lock size={9} /> : <Unlock size={9} />}
      {label}
    </button>
  );
}
