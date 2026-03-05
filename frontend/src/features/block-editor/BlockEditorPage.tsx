import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useBlockEditorStore } from '@/store/blockEditorStore';
import { useViewerStore } from '@/store';
import { siteZonesApi } from '@/services/api';
import { BlockEditorCanvas } from './BlockEditorCanvas';
import { BlockEditorHeader } from './BlockEditorHeader';
import { BlockPropertiesPanel } from './BlockPropertiesPanel';
import { StatsPanel } from './StatsPanel';
import { EditorToolbar } from './EditorToolbar';
import { useBlockEditorKeyboard } from './hooks/useBlockEditorKeyboard';

export function BlockEditorPage() {
  const { id: projectId, zoneId } = useParams<{ id: string; zoneId: string }>();
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const { initEditor, resetEditor, editedLayout, zone } = useBlockEditorStore();
  const { layoutPreview, clearLayoutPreview, clearLockedLayers } = useViewerStore();

  useBlockEditorKeyboard();

  // Initialize editor from layout preview data in Zustand store
  useEffect(() => {
    if (!projectId || !zoneId) return;

    const loadData = async () => {
      setLoading(true);
      try {
        // Get zone data
        const zones = await siteZonesApi.list(projectId);
        const zone = zones.find((z) => z.id === zoneId);
        if (!zone) {
          toast.error('Zone not found');
          navigate(`/projects/${projectId}`);
          return;
        }

        // Get layout options - either from store or generate new ones
        let options = layoutPreview?.zoneId === zoneId ? layoutPreview.options : [];
        if (options.length === 0) {
          // No cached options, generate new ones
          const response = await siteZonesApi.previewLayouts(zoneId);
          options = response.options;
        }

        if (options.length === 0) {
          toast.error('No layout options available');
          navigate(`/projects/${projectId}`);
          return;
        }

        initEditor(projectId, zone, options);
      } catch (err: any) {
        toast.error(err?.response?.data?.detail || 'Failed to load editor');
        navigate(`/projects/${projectId}`);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    return () => resetEditor();
  }, [projectId, zoneId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Track container size for responsive SVG
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

  const handleBack = useCallback(() => {
    navigate(`/projects/${projectId}`);
  }, [navigate, projectId]);

  const handleSave = useCallback(async () => {
    if (!editedLayout || !zoneId) return;
    setIsSaving(true);
    try {
      // Save layout to zone properties
      await siteZonesApi.update(zoneId, {
        properties: {
          ...(zone?.properties || {}),
          _saved_layout: editedLayout,
        },
      });
      toast.success('Layout saved');
    } catch {
      toast.error('Failed to save layout');
    } finally {
      setIsSaving(false);
    }
  }, [editedLayout, zoneId, zone]);

  const handleGenerate3D = useCallback(async () => {
    if (!editedLayout || !zoneId || !projectId) return;
    setIsGenerating(true);
    try {
      // 1. Apply the layout (creates Building records)
      await siteZonesApi.applyLayout(zoneId, 0, editedLayout);

      // 2. Queue 3D generation for all buildings
      const result = await siteZonesApi.generateAll(projectId);

      clearLayoutPreview();
      clearLockedLayers();

      toast.success(`${result.buildings_created} buildings created, ${result.generations_queued} queued for 3D generation`);

      // 3. Navigate to 3D viewer
      navigate(`/projects/${projectId}/viewer`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to generate 3D');
    } finally {
      setIsGenerating(false);
    }
  }, [editedLayout, zoneId, projectId, navigate, clearLayoutPreview, clearLockedLayers]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-primary-950">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={28} className="animate-spin text-indigo-400" />
          <span className="text-sm text-neutral-400">Loading block editor...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-primary-950">
      <BlockEditorHeader
        onBack={handleBack}
        onSave={handleSave}
        onGenerate3D={handleGenerate3D}
        isSaving={isSaving}
        isGenerating={isGenerating}
      />
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
    </div>
  );
}
