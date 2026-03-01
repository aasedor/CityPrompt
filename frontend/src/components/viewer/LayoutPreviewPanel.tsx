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
  const {
    layoutPreview, setLayoutPreview, clearLayoutPreview, setActivePreviewIndex,
    setPreviewImageUrl, setLightboxImage,
    lockedLayers, toggleLayerLock, clearLockedLayers,
  } = useViewerStore();
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [renderingIndices, setRenderingIndices] = useState<Set<number>>(new Set());
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
  }, [zone.id]);

  const renderOption = async (idx: number, option: LayoutOption) => {
    setRenderingIndices((prev) => new Set(prev).add(idx));
    try {
      const result = await siteZonesApi.renderLayoutPreview(zone.id, option);
      // Store image URL in Zustand store so it persists across navigation
      setPreviewImageUrl(idx, result.image_url);
    } catch {
      // Silently fail — SVG fallback will show
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
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
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
        <span className="text-xs font-semibold text-gray-700">Layout Options</span>
        <div className="flex items-center gap-2">
          {renderingCount > 0 && (
            <span className="flex items-center gap-1 text-[10px] text-purple-500">
              <Loader2 size={9} className="animate-spin" />
              Rendering {renderingCount}...
            </span>
          )}
          <button
            onClick={handlePreview}
            disabled={loading}
            className="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] text-indigo-600 hover:bg-indigo-50"
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
          onRerender={() => renderOption(idx, opt)}
          onImageClick={previewImages[idx] ? () => setLightboxImage(previewImages[idx]) : undefined}
        />
      ))}

      {/* Expanded view for active option */}
      {activeOption && (
        <div className="rounded-lg border border-indigo-200 bg-indigo-50/30 p-2">
          {previewImages[activeIndex] ? (
            <img
              src={previewImages[activeIndex]}
              alt="AI-rendered layout preview"
              className="w-full rounded cursor-zoom-in"
              onClick={() => setLightboxImage(previewImages[activeIndex])}
            />
          ) : renderingIndices.has(activeIndex) ? (
            <div className="flex h-[200px] items-center justify-center rounded bg-gray-100">
              <div className="flex flex-col items-center gap-2">
                <Loader2 size={20} className="animate-spin text-purple-500" />
                <span className="text-[10px] text-gray-500">Rendering realistic preview...</span>
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
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-2 space-y-1.5">
          <span className="text-[10px] font-semibold text-gray-600 uppercase tracking-wide">Lock Layers</span>
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
              className="flex w-full items-center justify-center gap-1.5 rounded bg-amber-500 px-2 py-1 text-[10px] font-medium text-white hover:bg-amber-600 disabled:opacity-50"
            >
              {regenerating ? <Loader2 size={10} className="animate-spin" /> : <RefreshCw size={10} />}
              {regenerating ? 'Regenerating...' : 'Regenerate Unlocked Layers'}
            </button>
          )}
        </div>
      )}

      <button
        onClick={handleApply}
        disabled={applying}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-green-600 px-3 py-2 text-xs font-semibold text-white hover:bg-green-700 disabled:opacity-50"
      >
        {applying ? <Loader2 size={12} className="animate-spin" /> : <Check size={12} />}
        {applying ? 'Applying...' : 'Apply This Layout'}
      </button>

      <button
        onClick={() => { clearLayoutPreview(); clearLockedLayers(); }}
        className="w-full rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-50"
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
  onRerender?: () => void;
  onImageClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`w-full cursor-pointer rounded-lg border p-2 text-left transition-all ${
        isActive
          ? 'border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className={`text-xs font-semibold ${isActive ? 'text-indigo-700' : 'text-gray-700'}`}>
          {option.option_label}
        </span>
        <span className="text-[10px] text-gray-400">
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
          />
          {onRerender && (
            <button
              onClick={(e) => { e.stopPropagation(); onRerender(); }}
              className="absolute bottom-1 right-1 rounded bg-black/50 p-1 text-white/80 hover:bg-black/70 hover:text-white"
              title="Re-render preview"
            >
              <RefreshCw size={10} />
            </button>
          )}
        </div>
      ) : isRendering ? (
        <div className="flex h-[140px] items-center justify-center rounded bg-gray-100">
          <div className="flex flex-col items-center gap-1.5">
            <Loader2 size={16} className="animate-spin text-purple-400" />
            <span className="text-[9px] text-gray-400">Rendering...</span>
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
              className="absolute bottom-1 right-1 flex items-center gap-1 rounded bg-purple-600/80 px-1.5 py-0.5 text-[9px] font-medium text-white hover:bg-purple-600"
            >
              <ImageIcon size={9} />
              Render
            </button>
          )}
        </div>
      )}

      {option.density_achieved && (
        <div className="mt-1 text-[10px] text-gray-400">
          {option.density_achieved} units/ha
        </div>
      )}
      <p className="mt-0.5 text-[10px] leading-tight text-gray-500 line-clamp-2">
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
          ? 'bg-amber-100 text-amber-700 border border-amber-300'
          : 'bg-gray-100 text-gray-500 border border-gray-200 hover:bg-gray-200'
      }`}
    >
      {isLocked ? <Lock size={9} /> : <Unlock size={9} />}
      {label}
    </button>
  );
}
