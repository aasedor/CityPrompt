import { useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback, useRef, useMemo, type RefObject } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ChevronDown, Undo2, Redo2, Save, Wand2, Grid3X3, Ruler, Lightbulb } from 'lucide-react';
import toast from 'react-hot-toast';
import { useBlockEditorStore } from '@/store/blockEditorStore';
import { useGenerationStore } from '@/store/generationStore';
import { useViewerStore } from '@/store';
import { siteZonesApi } from '@/services/api';
import { BlockEditorCanvas } from './BlockEditorCanvas';
import { BlockPropertiesPanel } from './BlockPropertiesPanel';
import { StatsPanel } from './StatsPanel';
import { EditorToolbar } from './EditorToolbar';
import { useBlockEditorKeyboard } from './hooks/useBlockEditorKeyboard';
import type { SiteZone, LayoutOption } from '@/types';

interface EmbeddedBlockEditorProps {
  projectId: string;
  zones: SiteZone[];
  onFinalized?: () => void;
}

export function EmbeddedBlockEditor({ projectId, zones, onFinalized }: EmbeddedBlockEditorProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 500 });
  const [loading, setLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeZoneId, setActiveZoneId] = useState<string | null>(null);

  const { initEditor, resetEditor, editedLayout, zone, zoneId: storeZoneId } = useBlockEditorStore();
  const { layoutPreview, clearLayoutPreview, clearLockedLayers } = useViewerStore();

  useBlockEditorKeyboard();

  // Prevent page scroll when mouse is over the block editor, but allow
  // native scroll inside the properties panel (which has overflow-y-auto).
  useEffect(() => {
    const el = wrapperRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      const target = e.target as HTMLElement;
      if (target.closest('[data-scrollable]')) return;
      e.preventDefault();
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, []);

  // Find zones that can be edited (building/residential/development_area)
  const editableZones = useMemo(() =>
    zones.filter((z) =>
      (z.zone_type === 'building' || z.zone_type === 'residential' || z.zone_type === 'development_area')
    ),
    [zones],
  );

  // Check if selected zone needs a description before layout generation
  const selectedZone = editableZones.find((z) => z.id === activeZoneId);
  const needsDescription = selectedZone && !selectedZone.properties?.description_text;

  // Auto-select first editable zone that has a description (ready for layout),
  // falling back to the first editable zone if none have descriptions
  useEffect(() => {
    if (editableZones.length > 0 && !activeZoneId) {
      const withDesc = editableZones.find((z) => z.properties?.description_text);
      setActiveZoneId((withDesc || editableZones[0]).id);
    }
  }, [editableZones, activeZoneId]);

  // Load layout options for selected zone
  useEffect(() => {
    if (!activeZoneId) return;
    const zoneForLoad = zones.find((z) => z.id === activeZoneId);
    if (!zoneForLoad) return;

    const loadData = async () => {
      const store = useBlockEditorStore.getState();

      // Skip if the store already has this zone's layout (e.g. tab switch back)
      if (store.zoneId === activeZoneId && store.editedLayout) {
        setLoading(false);
        return;
      }

      if (!zoneForLoad?.properties?.description_text) {
        setLoading(false);
        return;
      }

      // Check all caches BEFORE showing loading spinner

      // 1. Saved layout in zone properties
      const savedLayout = zoneForLoad.properties?._saved_layout as LayoutOption | undefined;
      if (savedLayout) {
        store.cacheLayout(activeZoneId, [savedLayout]);
        initEditor(projectId, zoneForLoad, [savedLayout]);
        return;
      }

      // 2. Zustand store cache (persists across component unmounts)
      const cached = store.getCachedLayout(activeZoneId);
      if (cached) {
        initEditor(projectId, zoneForLoad, cached);
        return;
      }

      // 3. Cached layout in zustand viewer store
      const cachedOptions = layoutPreview?.zoneId === activeZoneId ? layoutPreview.options : [];
      if (cachedOptions.length > 0) {
        store.cacheLayout(activeZoneId, cachedOptions);
        initEditor(projectId, zoneForLoad, cachedOptions);
        return;
      }

      // No cache — need to call the API (slow path)
      setLoading(true);
      try {
        const response = await siteZonesApi.previewLayouts(activeZoneId);
        const options = response.options;
        if (options.length === 0) {
          toast.error('No layout options generated');
          return;
        }
        store.cacheLayout(activeZoneId, options);
        initEditor(projectId, zoneForLoad, options);
      } catch (err: any) {
        toast.error(err?.response?.data?.detail || 'Failed to generate layouts');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [activeZoneId, projectId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Track container size
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setContainerSize({ width, height });
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);


  const handleSave = useCallback(async () => {
    if (!editedLayout || !activeZoneId) return;
    setIsSaving(true);
    try {
      // Uses save-layout endpoint which saves to properties AND updates building positions
      const saveResult = await siteZonesApi.saveLayout(activeZoneId, editedLayout);
      const parts = [];
      if (saveResult.buildings_updated) parts.push(`${saveResult.buildings_updated} updated`);
      if (saveResult.buildings_created) parts.push(`${saveResult.buildings_created} created`);
      if (saveResult.buildings_deleted) parts.push(`${saveResult.buildings_deleted} removed`);
      toast.success(`Layout saved${parts.length ? ' — ' + parts.join(', ') : ''}`);
      // Invalidate project query so 3D viewer gets updated building positions
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
    } catch {
      toast.error('Failed to save layout');
    } finally {
      setIsSaving(false);
    }
  }, [editedLayout, activeZoneId, queryClient, projectId]);

  const handleGenerate3D = useCallback(async () => {
    if (!editedLayout || !activeZoneId || !projectId) return;

    // Check if any buildings already have 3D models
    const projectData = queryClient.getQueryData<{ buildings?: { model_url?: string; name?: string }[] }>(['project', projectId]);
    const existingModels = projectData?.buildings?.filter((b) => b.model_url) ?? [];
    if (existingModels.length > 0) {
      const confirmed = window.confirm(
        `${existingModels.length} building${existingModels.length > 1 ? 's' : ''} already ${existingModels.length > 1 ? 'have' : 'has'} 3D models. Regenerating will replace them and use additional credits.\n\nContinue?`
      );
      if (!confirmed) return;
    }

    setIsGenerating(true);
    try {
      // Save layout first to ensure buildings are created/synced
      await siteZonesApi.saveLayout(activeZoneId, editedLayout);
      const result = await siteZonesApi.generateAll(projectId);
      clearLayoutPreview();
      clearLockedLayers();
      // Seed generation store so the progress bar shows prominently
      if (result.queued_buildings && result.queued_buildings.length > 0) {
        useGenerationStore.getState().startBatch(projectId, result.queued_buildings);
      }
      toast.success(`${result.generations_queued} buildings queued for 3D generation`);
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      onFinalized?.();
      navigate(`/projects/${projectId}/viewer`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to generate 3D');
    } finally {
      setIsGenerating(false);
    }
  }, [editedLayout, activeZoneId, projectId, navigate, clearLayoutPreview, clearLockedLayers, onFinalized, queryClient]);

  if (editableZones.length === 0) {
    return (
      <div className="flex h-[500px] items-center justify-center text-neutral-400 text-sm">
        No editable zones found. Draw a building, residential, or development area zone in the Master Plan first.
      </div>
    );
  }

  return (
    <div ref={wrapperRef} className="flex h-[500px] flex-col bg-primary-950 rounded-b-xl overflow-hidden">
      {/* Editor header with zone picker integrated */}
      {!loading && editedLayout && (
        <div className="flex items-center justify-between border-b border-white/[0.08] bg-primary-950/95 backdrop-blur-xl px-4 py-2">
          {/* Left: Zone picker + info */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <select
                value={activeZoneId || ''}
                onChange={(e) => setActiveZoneId(e.target.value)}
                className="appearance-none rounded-lg border border-white/[0.1] bg-white/[0.05] pl-3 pr-7 py-1.5 text-xs text-white font-medium focus:border-indigo-400/50 focus:outline-none cursor-pointer"
              >
                {editableZones.map((z) => (
                  <option key={z.id} value={z.id} className="bg-primary-950 text-white">
                    {z.name || z.zone_type}
                  </option>
                ))}
              </select>
              <ChevronDown size={12} className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-neutral-400" />
            </div>
            <span className="text-[10px] text-neutral-500">{editedLayout.buildings.length} blocks</span>
          </div>

          {/* Spacer */}
          <div />

          {/* Right: Tools + Actions */}
          <EditorControls
            onSave={handleSave}
            onGenerate3D={handleGenerate3D}
            isSaving={isSaving}
            isGenerating={isGenerating}
          />
        </div>
      )}

      {/* Nudge: zone needs a description */}
      {needsDescription && !loading && !editedLayout && (
        <div className="flex flex-1 items-center justify-center">
          <div className="flex flex-col items-center gap-4 max-w-md text-center px-8">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10 ring-1 ring-amber-500/20">
              <Lightbulb size={28} className="text-amber-400" />
            </div>
            <h3 className="text-base font-semibold text-white">Add a Description to Get Started</h3>
            <p className="text-sm text-neutral-400 leading-relaxed">
              Go back to the <span className="text-indigo-300 font-medium">Master Plan</span> tab, select the
              <span className="text-white font-medium"> {selectedZone?.name || 'zone'}</span>, and add a description
              (e.g. "Modern residential complex with 8 units, shared courtyard, underground parking").
              The AI will use it to generate building layout options.
            </p>
            <div className="flex items-center gap-2 rounded-lg bg-white/[0.04] border border-white/[0.08] px-4 py-2.5 text-xs text-neutral-300">
              <span className="text-amber-400 font-bold">Tip:</span>
              The more detail you provide, the better the AI layout will be.
            </div>
          </div>
        </div>
      )}

      {/* Canvas area */}
      {loading ? (
        <div className="flex flex-1 items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <Loader2 size={24} className="animate-spin text-indigo-400" />
            <span className="text-xs text-neutral-400">Generating layout options...</span>
          </div>
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          <div ref={containerRef} className="relative flex-1">
            <BlockEditorCanvas
              width={containerSize.width}
              height={containerSize.height}
              allZones={editableZones}
              onSelectZone={setActiveZoneId}
            />
            <StatsPanel />
            <EditorToolbar />
          </div>
          <BlockPropertiesPanel />
        </div>
      )}
    </div>
  );
}

function OptionTabs() {
  const { options, activeOptionIndex, switchOption } = useBlockEditorStore();
  return (
    <div className="flex items-center gap-1">
      {options.map((opt, idx) => (
        <button
          key={idx}
          onClick={() => switchOption(idx)}
          className={`rounded-lg px-3 py-1 text-xs font-medium transition-all ${idx === activeOptionIndex ? 'bg-indigo-500/20 text-indigo-300 ring-1 ring-indigo-400/30' : 'text-neutral-400 hover:bg-white/[0.06] hover:text-neutral-200'}`}
        >
          {opt.option_label || `Option ${idx + 1}`}
        </button>
      ))}
    </div>
  );
}

function EditorControls({
  onSave, onGenerate3D, isSaving, isGenerating,
}: { onSave: () => void; onGenerate3D: () => void; isSaving: boolean; isGenerating: boolean }) {
  const {
    undo, redo, undoStack, redoStack, editedLayout,
    showGrid, toggleGrid, showDimensions, toggleDimensions,
  } = useBlockEditorStore();
  const buildingCount = editedLayout?.buildings.length ?? 0;

  return (
    <div className="flex items-center gap-2">
      <button onClick={toggleGrid}
        className={`rounded p-1.5 transition-colors ${showGrid ? 'bg-white/10 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
        title="Toggle grid"><Grid3X3 size={14} /></button>
      <button onClick={toggleDimensions}
        className={`rounded p-1.5 transition-colors ${showDimensions ? 'bg-white/10 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
        title="Toggle dimensions"><Ruler size={14} /></button>
      <div className="h-5 w-px bg-white/[0.1]" />
      <button onClick={undo} disabled={undoStack.length === 0}
        className="rounded p-1.5 text-neutral-400 hover:bg-white/[0.06] hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
        title="Undo (Ctrl+Z)"><Undo2 size={14} /></button>
      <button onClick={redo} disabled={redoStack.length === 0}
        className="rounded p-1.5 text-neutral-400 hover:bg-white/[0.06] hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
        title="Redo (Ctrl+Shift+Z)"><Redo2 size={14} /></button>
      <div className="h-5 w-px bg-white/[0.1]" />
      <button onClick={onSave} disabled={isSaving}
        className="flex items-center gap-1.5 rounded-lg bg-white/[0.08] px-3 py-1.5 text-xs font-medium text-neutral-200 hover:bg-white/[0.12] disabled:opacity-50">
        <Save size={12} />{isSaving ? 'Saving...' : 'Save'}
      </button>
      <button onClick={onGenerate3D} disabled={isGenerating || buildingCount === 0}
        className="flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 px-4 py-1.5 text-xs font-semibold text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-400 hover:to-purple-400 disabled:opacity-50 transition-all">
        <Wand2 size={13} />{isGenerating ? 'Generating...' : 'Generate 3D'}
      </button>
    </div>
  );
}
