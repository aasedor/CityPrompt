import { useState } from 'react';
import { Loader2, LayoutGrid, RefreshCw, Check, Lock, Unlock } from 'lucide-react';
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
}

export function LayoutPreviewPanel({ zone, onApplied, referenceContext }: LayoutPreviewPanelProps) {
  const {
    layoutPreview, setLayoutPreview, clearLayoutPreview, setActivePreviewIndex,
    lockedLayers, toggleLayerLock, clearLockedLayers,
  } = useViewerStore();
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [regenerating, setRegenerating] = useState(false);

  const isPreviewActive = layoutPreview?.zoneId === zone.id;
  const options = isPreviewActive ? layoutPreview!.options : [];
  const activeIndex = isPreviewActive ? layoutPreview!.activeIndex : 0;
  const activeOption = options[activeIndex];

  const handlePreview = async () => {
    setLoading(true);
    try {
      const response = await siteZonesApi.previewLayouts(zone.id);
      setLayoutPreview(zone.id, response.options);
      clearLockedLayers();
      toast.success(`Generated ${response.options.length} layout options`);
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
    try {
      const response = await siteZonesApi.regenerateLayout(zone.id, lockedLayers);
      setLayoutPreview(zone.id, response.options);
      toast.success(`Regenerated ${response.options.length} layout options (locked layers preserved)`);
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

  // Previewing — show option cards with diagrams
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-700">Layout Options</span>
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

      {options.map((opt, idx) => (
        <OptionCard
          key={idx}
          option={opt}
          zone={zone}
          isActive={idx === activeIndex}
          onClick={() => setActivePreviewIndex(idx)}
          referenceContext={referenceContext}
          lockedLayers={lockedLayers}
        />
      ))}

      {/* Expanded diagram for active option */}
      {activeOption && (
        <div className="rounded-lg border border-indigo-200 bg-indigo-50/30 p-2">
          <SitePlanDiagram
            zone={zone}
            option={activeOption}
            referenceContext={referenceContext}
            lockedLayers={lockedLayers}
            width={270}
            height={200}
            showLabels
            showDimensions
          />
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
}: {
  option: LayoutOption;
  zone: SiteZone;
  isActive: boolean;
  onClick: () => void;
  referenceContext?: OSMContext | null;
  lockedLayers?: LockedLayers | null;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-lg border p-2 text-left transition-all ${
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
      <SitePlanDiagram
        zone={zone}
        option={option}
        referenceContext={referenceContext}
        lockedLayers={isActive ? lockedLayers : undefined}
        width={250}
        height={140}
        showLabels={false}
        showDimensions={false}
      />
      {option.density_achieved && (
        <div className="mt-1 text-[10px] text-gray-400">
          {option.density_achieved} units/ha
        </div>
      )}
      <p className="mt-0.5 text-[10px] leading-tight text-gray-500 line-clamp-2">
        {option.reasoning}
      </p>
    </button>
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
