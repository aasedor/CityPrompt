import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ChevronDown, Undo2, Redo2, Save, Wand2, Grid3X3, Ruler } from 'lucide-react';
import toast from 'react-hot-toast';
import { useBlockEditorStore } from '@/store/blockEditorStore';
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
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 500 });
  const [loading, setLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeZoneId, setActiveZoneId] = useState<string | null>(null);

  const { initEditor, resetEditor, editedLayout, zone } = useBlockEditorStore();
  const { layoutPreview, clearLayoutPreview, clearLockedLayers } = useViewerStore();

  useBlockEditorKeyboard();

  // Find zones that can be edited (building/residential/development_area with descriptions)
  const editableZones = useMemo(() =>
    zones.filter((z) =>
      (z.zone_type === 'building' || z.zone_type === 'residential' || z.zone_type === 'development_area') &&
      z.properties?.description_text
    ),
    [zones],
  );

  // Auto-select first editable zone
  useEffect(() => {
    if (editableZones.length > 0 && !activeZoneId) {
      setActiveZoneId(editableZones[0].id);
    }
  }, [editableZones, activeZoneId]);

  // Load layout options for selected zone
  useEffect(() => {
    if (!activeZoneId) return;
    const selectedZone = zones.find((z) => z.id === activeZoneId);
    if (!selectedZone) return;

    const loadData = async () => {
      setLoading(true);
      try {
        // 1. Check for saved layout in zone properties
        const savedLayout = selectedZone.properties?._saved_layout as LayoutOption | undefined;
        if (savedLayout) {
          initEditor(projectId, selectedZone, [savedLayout]);
          setLoading(false);
          return;
        }

        // 2. Check for cached layout in zustand store
        let options = layoutPreview?.zoneId === activeZoneId ? layoutPreview.options : [];

        // 3. Only call previewLayouts if no saved or cached layout
        if (options.length === 0) {
          const response = await siteZonesApi.previewLayouts(activeZoneId);
          options = response.options;
        }
        if (options.length === 0) {
          toast.error('No layout options generated');
          setLoading(false);
          return;
        }
        initEditor(projectId, selectedZone, options);
      } catch (err: any) {
        toast.error(err?.response?.data?.detail || 'Failed to generate layouts');
      } finally {
        setLoading(false);
      }
    };

    loadData();
    return () => resetEditor();
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
      await siteZonesApi.saveLayout(activeZoneId, editedLayout);
      toast.success('Layout saved — building positions updated');
    } catch {
      toast.error('Failed to save layout');
    } finally {
      setIsSaving(false);
    }
  }, [editedLayout, activeZoneId]);

  const handleGenerate3D = useCallback(async () => {
    if (!editedLayout || !activeZoneId || !projectId) return;
    setIsGenerating(true);
    try {
      await siteZonesApi.applyLayout(activeZoneId, 0, editedLayout);
      const result = await siteZonesApi.generateAll(projectId);
      clearLayoutPreview();
      clearLockedLayers();
      toast.success(`${result.buildings_created} buildings created, ${result.generations_queued} queued for 3D generation`);
      onFinalized?.();
      navigate(`/projects/${projectId}/viewer`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to generate 3D');
    } finally {
      setIsGenerating(false);
    }
  }, [editedLayout, activeZoneId, projectId, navigate, clearLayoutPreview, clearLockedLayers, onFinalized]);

  if (editableZones.length === 0) {
    return (
      <div className="flex h-[500px] items-center justify-center text-neutral-400 text-sm">
        No editable zones found. Draw building or residential zones with descriptions in the Master Plan first.
      </div>
    );
  }

  return (
    <div className="flex h-[500px] flex-col bg-primary-950 rounded-b-xl overflow-hidden">
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

          {/* Center: Option tabs */}
          <OptionTabs />

          {/* Right: Tools + Actions */}
          <EditorControls
            onSave={handleSave}
            onGenerate3D={handleGenerate3D}
            isSaving={isSaving}
            isGenerating={isGenerating}
          />
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
