import { useState, useCallback, useRef, useEffect, type PointerEvent as ReactPointerEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ArrowLeft, Camera, CheckCircle, Share2, MapPin, FileDown, Sparkles, Trash2 } from 'lucide-react';
import { projectsApi, rendersApi, resolveApiFileUrl } from '@/services/api';
import type { SavedRender } from '@/types';
import { AIGenerateModal } from '@/components/buildings/AIGenerateModal';
import { AddBuildingModal } from '@/components/buildings/AddBuildingModal';
import { ShareModal } from '@/components/sharing/ShareModal';
import { SitePlannerMap } from '@/components/viewer/SitePlannerMap';
import { SitePlannerToolbar } from '@/components/viewer/SitePlannerToolbar';
import { HistoryPanel } from '@/components/viewer/HistoryPanel';
import { GlobeSitePlannerMap } from '@/components/viewer/globe/GlobeSitePlannerMap';
import { GlobeAIRenderPanel } from '@/components/viewer/globe/GlobeAIRenderPanel';
import { useGlobeAIRender } from '@/components/viewer/globe/useGlobeAIRender';
import { useGlobeCamera } from '@/components/viewer/globe/useGlobeCamera';
import { ZonePropertiesPanel } from '@/components/viewer/ZonePropertiesPanel';
import { AIRenderPanel } from '@/components/viewer/AIRenderPanel';
import { RenderResultModal } from '@/components/viewer/RenderResultModal';
import { ZoneLegend } from '@/components/viewer/ZoneLegend';
import { StreetViewPanel } from '@/components/viewer/StreetViewPanel';
import { WorkflowStepper } from '@/components/viewer/WorkflowStepper';
import { OnboardingTour } from '@/components/viewer/OnboardingTour';
import type { AIRenderResult } from '@/components/viewer/useAIRender';
import { useViewerStore } from '@/store';
import { useSiteZones } from '@/hooks/useSiteZones';
import { useUndoRedoKeyboard } from '@/hooks/useUndoRedoKeyboard';
import { rebufferRoadOnUpdate } from '@/utils/roadGeometry';
import { ImageLightbox } from '@/components/ui/ImageLightbox';

const GLOBE_RENDER_PANEL_WIDTH = 704;

export function ProjectViewPage() {
  const { id } = useParams<{ id: string }>();
  const [showAddBuilding, setShowAddBuilding] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [aiGenerateBuildingId, setAiGenerateBuildingId] = useState<string | null>(null);
  const [savedRenders, setSavedRenders] = useState<SavedRender[]>([]);
  const [renderLightbox, setRenderLightbox] = useState<SavedRender | null>(null);
  const [showTour, setShowTour] = useState(false);
  const [showGlobeRender, setShowGlobeRender] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [measureActive, setMeasureActive] = useState(false);
  const [globeRenderPosition, setGlobeRenderPosition] = useState<{ x: number; y: number } | null>(null);
  const [isDraggingGlobeRender, setIsDraggingGlobeRender] = useState(false);
  const [globeRefs, setGlobeRefs] = useState<{ canvas: HTMLCanvasElement; camera: any; terrainHeight: number } | null>(null);
  const queryClient = useQueryClient();
  const prevStatusMap = useRef<Record<string, string>>({});
  const globeRenderDragRef = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(null);

  // Globe street view capture
  const { captureStreetView } = useGlobeAIRender();
  const { flyToStreetLevel, restoreAerialView, saveCameraState } = useGlobeCamera();

  const handleGlobeStreetCapture = useCallback(async (): Promise<string | null> => {
    if (!globeRefs?.canvas || !globeRefs?.camera) return null;
    const pegman = useViewerStore.getState().streetViewPegman;
    if (!pegman?.position) return null;
    const [lng, lat] = pegman.position;
    return captureStreetView(
      globeRefs.canvas, globeRefs.camera,
      lat, lng, pegman.angle,
      pegman.terrainHeight ?? globeRefs.terrainHeight,
      flyToStreetLevel, restoreAerialView, saveCameraState,
    );
  }, [globeRefs, captureStreetView, flyToStreetLevel, restoreAerialView, saveCameraState]);

  // Register Ctrl+Z / Ctrl+Shift+Z keyboard shortcuts for undo/redo
  useUndoRedoKeyboard();

  // Site planner store + zone CRUD + workflow
  const {
    setSitePlannerActive,
    setActiveSitePlannerTool,
    selectedZoneId,
    selectZone,
    mapInstance,
    workflowStep,
    setWorkflowStep,
    settings,
    activeSitePlannerTool,
  } = useViewerStore();

  const {
    siteZones,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  } = useSiteZones(id);

  const selectedZone = siteZones.find((z) => z.id === selectedZoneId) || null;

  const hasEditableZones = siteZones.some((z) =>
    z.zone_type !== 'site_boundary' && z.coordinates && z.coordinates.length >= 3
  );

  // Activate site planner on mount, pre-select buildings tool, reset workflow step
  // Load saved renders for this project
  useEffect(() => {
    if (!id) return;
    rendersApi.list(id).then(setSavedRenders).catch(() => {});
  }, [id]);

  useEffect(() => {
    setSitePlannerActive(true);
    setActiveSitePlannerTool(window.matchMedia('(min-width: 640px)').matches ? 'building' : null);
    setWorkflowStep(1);
    return () => {
      setSitePlannerActive(false);
      setActiveSitePlannerTool(null);
      selectZone(null);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setSitePlannerActive, setActiveSitePlannerTool, selectZone, setWorkflowStep, id]);

  const handleZoneSelected = useCallback((zoneId: string | null) => {
    selectZone(zoneId);
  }, [selectZone]);

  const clampGlobeRenderPosition = useCallback((position: { x: number; y: number }) => {
    if (typeof window === 'undefined') return position;
    const panelWidth = Math.min(GLOBE_RENDER_PANEL_WIDTH, Math.max(320, window.innerWidth - 32));
    return {
      x: Math.min(Math.max(12, position.x), Math.max(12, window.innerWidth - panelWidth - 12)),
      y: Math.min(Math.max(12, position.y), Math.max(12, window.innerHeight - 96)),
    };
  }, []);

  const getDefaultGlobeRenderPosition = useCallback(() => {
    if (typeof window === 'undefined') return { x: 320, y: 420 };
    const panelWidth = Math.min(GLOBE_RENDER_PANEL_WIDTH, Math.max(320, window.innerWidth - 32));
    const panelHeight = Math.min(420, window.innerHeight * 0.44);
    return clampGlobeRenderPosition({
      x: (window.innerWidth - panelWidth) / 2,
      y: window.innerHeight - panelHeight - 16,
    });
  }, [clampGlobeRenderPosition]);

  const handleGlobeRenderDragStart = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) return;
    event.preventDefault();

    const handleRect = event.currentTarget.getBoundingClientRect();
    const origin = globeRenderPosition ?? (
      handleRect.width > 0 && handleRect.height > 0
        ? clampGlobeRenderPosition({ x: handleRect.left, y: handleRect.top })
        : getDefaultGlobeRenderPosition()
    );
    globeRenderDragRef.current = {
      startX: event.clientX,
      startY: event.clientY,
      originX: origin.x,
      originY: origin.y,
    };
    setGlobeRenderPosition(origin);
    setIsDraggingGlobeRender(true);

    const handlePointerMove = (moveEvent: PointerEvent) => {
      const drag = globeRenderDragRef.current;
      if (!drag) return;
      setGlobeRenderPosition(clampGlobeRenderPosition({
        x: drag.originX + moveEvent.clientX - drag.startX,
        y: drag.originY + moveEvent.clientY - drag.startY,
      }));
    };

    const handlePointerUp = () => {
      globeRenderDragRef.current = null;
      setIsDraggingGlobeRender(false);
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      window.removeEventListener('pointercancel', handlePointerUp);
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);
    window.addEventListener('pointercancel', handlePointerUp);
  }, [clampGlobeRenderPosition, getDefaultGlobeRenderPosition, globeRenderPosition]);

  useEffect(() => {
    const handleResize = () => {
      setGlobeRenderPosition((position) => position ? clampGlobeRenderPosition(position) : position);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [clampGlobeRenderPosition]);

  const handleMeasureModeChange = useCallback((active: boolean) => {
    setMeasureActive(active);
    if (active) {
      setShowGlobeRender(false);
      selectZone(null);
      setActiveSitePlannerTool(null);
    }
  }, [selectZone, setActiveSitePlannerTool]);

  const handleToggleHistory = useCallback(() => {
    setShowGlobeRender(false);
    setMeasureActive(false);
    setShowHistory((open) => !open);
  }, []);

  const handleOpenGlobeRender = useCallback(() => {
    setShowHistory(false);
    setMeasureActive(false);
    setGlobeRenderPosition(null);
    setShowGlobeRender(true);
  }, []);

  const prepareForAIRenderCapture = useCallback(async () => {
    if (useViewerStore.getState().selectedZoneId) {
      selectZone(null);
    }
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  }, [selectZone]);

  // ── AI Render state ────────────────────────────────────────────────
  const [aiRenderResult, setAiRenderResult] = useState<AIRenderResult | null>(null);
  const [showRenderModal, setShowRenderModal] = useState(false);
  const [renderPreviews, setRenderPreviews] = useState<AIRenderResult[]>([]);
  const [renderModalSelectedIdx, setRenderModalSelectedIdx] = useState<number | null>(null);
  const [isGeneratingFull, setIsGeneratingFull] = useState(false);
  const [fullRenderResult, setFullRenderResult] = useState<AIRenderResult | null>(null);
  const [renderProgressMessage, setRenderProgressMessage] = useState('');

  /** Handle AI render result — overlay on map */
  const handleAIRenderComplete = useCallback((result: AIRenderResult) => {
    setAiRenderResult(result);
    console.log('[AIRender] Render complete:', result.imageUrl);

    if (mapInstance) {
      const map = mapInstance as any;
      try {
        if (map.getLayer('ai-render-overlay')) map.removeLayer('ai-render-overlay');
        if (map.getSource('ai-render-source')) map.removeSource('ai-render-source');

        map.addSource('ai-render-source', {
          type: 'image',
          url: result.imageUrl,
          coordinates: result.bounds,
        });
        map.addLayer({
          id: 'ai-render-overlay',
          type: 'raster',
          source: 'ai-render-source',
          paint: { 'raster-opacity': 0.92, 'raster-fade-duration': 300 },
        });
      } catch (err) {
        console.warn('[AIRender] Could not overlay on map:', err);
      }
    }
  }, [mapInstance]);

  /** Clear AI render overlay */
  const handleClearAIOverlay = useCallback(() => {
    setAiRenderResult(null);
    if (mapInstance) {
      const map = mapInstance as any;
      try {
        if (map.getLayer('ai-render-overlay')) map.removeLayer('ai-render-overlay');
        if (map.getSource('ai-render-source')) map.removeSource('ai-render-source');
      } catch { /* ignore */ }
    }
  }, [mapInstance]);

  /** When AIRenderPanel produces previews, open the full-screen modal */
  const handlePreviewsReady = useCallback((previews: AIRenderResult[]) => {
    setRenderPreviews(previews);
    setRenderModalSelectedIdx(null);
    setFullRenderResult(null);
    setShowRenderModal(true);
  }, []);

  /** When user selects a preview in the modal */
  const handleModalSelectPreview = useCallback(async (index: number) => {
    setRenderModalSelectedIdx(index);
    const preview = renderPreviews[index];
    if (!preview?.seed || !mapInstance) return;

    setIsGeneratingFull(true);
    setRenderProgressMessage('Rendering full quality from current view...');
    try {
      setFullRenderResult(preview);
    } finally {
      setIsGeneratingFull(false);
      setRenderProgressMessage('');
    }
  }, [renderPreviews, mapInstance]);

  /** Close the render modal */
  const handleCloseRenderModal = useCallback(() => {
    setShowRenderModal(false);
    setRenderPreviews([]);
    setRenderModalSelectedIdx(null);
    setFullRenderResult(null);
    setRenderProgressMessage('');
  }, []);

  const handleAIRenderCompleteWithModal = useCallback((result: AIRenderResult) => {
    handleAIRenderComplete(result);
    if (showRenderModal) {
      setFullRenderResult(result);
      setIsGeneratingFull(false);
      setRenderProgressMessage('');
    }
  }, [handleAIRenderComplete, showRenderModal]);

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      const hasGenerating = data.buildings?.some(
        (b: { generation_status?: string }) => b.generation_status === 'generating'
      );
      return hasGenerating ? 3000 : false;
    },
  });

  // Toast when document processing completes or fails
  useEffect(() => {
    if (!project?.documents) return;
    for (const doc of project.documents) {
      const prev = prevStatusMap.current[doc.id];
      if (prev && prev !== doc.processing_status) {
        if (doc.processing_status === 'completed') {
          toast.success(`"${doc.filename}" processed - buildings extracted`);
        } else if (doc.processing_status === 'failed') {
          toast.error(`"${doc.filename}" processing failed`);
        }
      }
      prevStatusMap.current[doc.id] = doc.processing_status;
    }
  }, [project?.documents]);

  if (isLoading) return <div className="text-center text-primary-950/50">Loading project...</div>;
  if (!project) return <div className="text-center text-primary-950/50">Project not found</div>;

  // --- Globe mode: full-screen Google 3D Tiles ---
  if (settings.mapMode === 'globe') {
    return (
      <div className="fixed inset-0 z-50 bg-black" style={{ top: 0 }}>
        <GlobeSitePlannerMap
          latitude={project.location?.latitude}
          longitude={project.location?.longitude}
          siteZones={siteZones}
          onZoneCreated={handleZoneCreated}
          onZoneUpdated={handleZoneUpdated}
          onZoneSelected={(zoneId) => { if (zoneId) selectZone(zoneId); else selectZone(null); }}
          onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
          onGlobeReady={setGlobeRefs}
          measureModeActive={measureActive}
          onMeasureModeChange={handleMeasureModeChange}
        />

        {/* Toolbar — hidden on phones during focused vertex placement. */}
        <div className={`absolute inset-x-3 z-30 overflow-y-auto overscroll-contain sm:inset-x-auto sm:left-4 sm:top-[272px] sm:bottom-4 sm:w-64 sm:max-h-none sm:overflow-visible ${activeSitePlannerTool ? 'hidden sm:block' : 'bottom-3 max-h-[38vh]'}`}>
          <SitePlannerToolbar
            layout="sidebar"
            isGlobeMode
            onToggleHistory={handleToggleHistory}
            historyOpen={showHistory}
            measureActive={measureActive}
            onMeasureModeChange={handleMeasureModeChange}
            bottomSlot={
              !showGlobeRender ? (
                <button
                  onClick={handleOpenGlobeRender}
                  className="flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-gradient-to-r from-[#28c7e8] to-[#c9ff3d] px-3 py-2.5 text-sm font-black uppercase text-[#151515] shadow-[4px_4px_0_0_#151515] transition hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_0_#151515]"
                >
                  <Camera size={16} />
                  AI Render
                </button>
              ) : null
            }
          />
        </div>

        {/* Zone properties panel */}
        {selectedZone && !showHistory && !measureActive && (
          <div className="absolute top-16 right-4 bottom-20 z-40 w-96 overflow-y-auto rounded-xl">
            <ZonePropertiesPanel
              key={selectedZone.id}
              zone={selectedZone}
              onUpdate={(zoneId, data) => {
                updateZone.mutate({ zoneId, data });
                if (siteZones) rebufferRoadOnUpdate(zoneId, data, siteZones, handleZoneUpdated);
              }}
              onDelete={(zoneId) => deleteZone.mutate(zoneId)}
              onClose={() => selectZone(null)}
              onAIGenerate={(buildingId) => setAiGenerateBuildingId(buildingId)}
              buildings={project.buildings}
              allZones={siteZones}
            />
          </div>
        )}

        {showHistory && !showGlobeRender && id && (
          <HistoryPanel
            projectId={id}
            siteZones={siteZones}
            onClose={() => setShowHistory(false)}
          />
        )}

        {/* AI Render expanded panel — bottom dock keeps the properties panel reachable. */}
        {showGlobeRender && (
          <div
            className="absolute z-30"
            style={{
              left: globeRenderPosition?.x ?? '50%',
              top: globeRenderPosition?.y,
              bottom: globeRenderPosition ? undefined : 48,
              transform: globeRenderPosition ? undefined : 'translateX(-50%)',
            }}
          >
            <div className="w-[44rem] max-w-[calc(100vw-2rem)]">
              <GlobeAIRenderPanel
                canvas={globeRefs?.canvas ?? null}
                camera={globeRefs?.camera ?? null}
                siteZones={siteZones}
                terrainHeight={globeRefs?.terrainHeight ?? 1045}
                projectId={project?.id}
                onBeforeRender={prepareForAIRenderCapture}
                isDragging={isDraggingGlobeRender}
                dragHandleProps={{
                  onPointerDown: handleGlobeRenderDragStart,
                }}
                onClose={() => setShowGlobeRender(false)}
              />
            </div>
          </div>
        )}

        {/* Back button */}
        <div className="absolute left-4 top-4 z-30 flex max-w-[calc(100vw-2rem)] items-center gap-3">
          <Link to="/projects" className="shrink-0 rounded-lg bg-gray-900/75 p-2 backdrop-blur-sm hover:bg-gray-900/90">
            <ArrowLeft size={18} className="text-white" />
          </Link>
          <span className="min-w-0 max-w-[calc(100vw-5.5rem)] truncate text-sm font-medium text-white/80 sm:max-w-none">
            {project.name}
          </span>
        </div>

        {/* Street View Panel — with globe 3D tiles capture */}
        <StreetViewPanel siteZones={siteZones} projectId={project?.id} globeCapture={handleGlobeStreetCapture} />

        {/* Double-click a variant to open large preview */}
        <ImageLightbox />
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
        <div className="flex items-center gap-3 sm:gap-4">
          <Link to="/projects" className="rounded-lg p-2 hover:bg-primary-950/[0.04]">
            <ArrowLeft size={20} />
          </Link>
          <div className="min-w-0 flex-1">
            <h1 className="truncate text-xl font-bold text-primary-950 sm:text-2xl">{project.name}</h1>
            {project.description && (
              <p className="mt-1 line-clamp-2 text-sm text-primary-950/50">{project.description}</p>
            )}
            {project.location?.address && (
              <p className="mt-1 flex items-center text-xs text-primary-950/50">
                <MapPin size={11} className="mr-1 flex-shrink-0" />
                {project.location.address}
              </p>
            )}
          </div>
        </div>
        <div className="flex gap-2 self-start sm:self-auto">
          <a
            href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/projects/${id}/report`}
            className="btn-secondary shrink-0"
          >
            <FileDown size={16} className="mr-2" />
            PDF Report
          </a>
          <button
            onClick={() => setShowShare(true)}
            className="btn-secondary shrink-0"
          >
            <Share2 size={16} className="mr-2" />
            Share
          </button>
        </div>
      </div>

      {/* Master Plan — 2-Step Workflow: Draw & Style → AI Render */}
      <section className="relative left-1/2 mt-6 w-screen max-w-none -translate-x-1/2 overflow-hidden border-y border-primary-950/[0.08] shadow-card sm:rounded-xl sm:border">
        {/* Workflow Stepper bar */}
        <WorkflowStepper
          currentStep={workflowStep}
          onStepClick={setWorkflowStep}
          hasRender={!!aiRenderResult}
        />

        <div className="relative h-[56vh] min-h-[430px] sm:h-[62vh] lg:h-[68vh]">
          <SitePlannerMap
            latitude={project.location?.latitude}
            longitude={project.location?.longitude}
            siteZones={siteZones}
            onZoneCreated={handleZoneCreated}
            onZoneUpdated={handleZoneUpdated}
            onZoneSelected={handleZoneSelected}
            onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
          />
          {/* GIS color legend */}
          <ZoneLegend siteZones={siteZones} />

          {/* Street View Panel */}
          <StreetViewPanel siteZones={siteZones} projectId={project?.id} />

          {showHistory && id && (
            <HistoryPanel
              projectId={id}
              siteZones={siteZones}
              onClose={() => setShowHistory(false)}
            />
          )}

          {/* Step 1: Zone properties panel */}
          {workflowStep === 1 && selectedZone && !showHistory && (
            <ZonePropertiesPanel
              key={selectedZone.id}
              zone={selectedZone}
              onUpdate={(zoneId, data) => {
                updateZone.mutate({ zoneId, data });
                // Re-buffer road polygon when width changes
                if (siteZones) {
                  rebufferRoadOnUpdate(zoneId, data, siteZones, handleZoneUpdated);
                }
              }}
              onDelete={(zoneId) => deleteZone.mutate(zoneId)}
              onClose={() => selectZone(null)}
              onAIGenerate={(buildingId) => setAiGenerateBuildingId(buildingId)}
              buildings={project.buildings}
              allZones={siteZones}
            />
          )}

          {/* Step 2: AI Render panel (right side of map) */}
          {workflowStep === 2 && mapInstance && (
            <AIRenderPanel
              mapRef={{ current: mapInstance as any }}
              siteZones={siteZones}
              onRenderComplete={handleAIRenderCompleteWithModal}
              onPreviewsReady={handlePreviewsReady}
              onClearOverlay={handleClearAIOverlay}
              projectId={project?.id}
              onBeforeRender={prepareForAIRenderCapture}
            />
          )}

          {/* AI render result indicator */}
          {aiRenderResult && (
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 bg-gray-900/90 backdrop-blur-sm rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg border border-green-700/50">
              <CheckCircle size={14} className="text-green-400" />
              <span className="text-sm text-green-300">AI render applied</span>
              <button
                onClick={handleClearAIOverlay}
                className="ml-2 text-xs text-gray-400 hover:text-white underline"
              >
                Clear
              </button>
            </div>
          )}
        </div>

        {/* Onboarding tour */}
        {workflowStep === 1 && <OnboardingTour forceShow={showTour} onComplete={() => setShowTour(false)} />}

        {/* Bottom toolbar — context-sensitive per step */}
        <div className="flex items-center justify-between gap-3 px-4 py-2 bg-gray-900 border-t border-gray-800">
          <div className="flex-1 min-w-0">
            <SitePlannerToolbar
              onShowGuide={() => setShowTour(true)}
              onToggleHistory={handleToggleHistory}
              historyOpen={showHistory}
            />
          </div>

          {/* Step 1: Render button to advance to step 2 */}
          {workflowStep === 1 && (
            <button
              data-tour="ai-render-btn"
              onClick={() => setWorkflowStep(2)}
              disabled={!hasEditableZones}
              className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              title={hasEditableZones ? 'Generate AI render from current view' : 'Draw zones first (buildings, parks, or streets)'}
            >
              <Sparkles size={16} />
              AI Render
            </button>
          )}

          {/* Step 2: Back to drawing */}
          {workflowStep === 2 && (
            <button
              onClick={() => setWorkflowStep(1)}
              className="rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-600"
            >
              ← Back to Drawing
            </button>
          )}
        </div>
      </section>

      <div className="mt-8 grid gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Saved Renders Gallery */}
          <section className="card">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-primary-950">
                <Sparkles size={20} />
                Saved Renders
              </h2>
              <span className="text-sm text-primary-950/50">
                {savedRenders.length} {savedRenders.length === 1 ? 'render' : 'renders'}
              </span>
            </div>
            {savedRenders.length > 0 ? (
              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
                {savedRenders.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => setRenderLightbox(r)}
                    className="group relative overflow-hidden rounded-lg border border-primary-950/[0.08] hover:border-primary-400 transition"
                  >
                    <img
                      src={resolveApiFileUrl(r.image_url)}
                      alt={r.prompt || 'Saved render'}
                      className="aspect-video w-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition" />
                    <div className="absolute bottom-0 left-0 right-0 px-2 py-1.5 opacity-0 group-hover:opacity-100 transition">
                      {r.style && (
                        <span className="rounded bg-white/20 px-1.5 py-0.5 text-[10px] font-medium text-white backdrop-blur-sm">
                          {r.style}
                        </span>
                      )}
                      <p className="mt-0.5 text-[10px] text-white/70 truncate">
                        {new Date(r.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-primary-950/50">
                No saved renders yet. Use the AI Render panel to generate images, then click "Save to Project".
              </p>
            )}
          </section>

          {showAddBuilding && (
            <AddBuildingModal
              projectId={project.id}
              projectLocation={project.location}
              onClose={() => setShowAddBuilding(false)}
            />
          )}
          {showShare && (
            <ShareModal projectId={project.id} projectName={project.name} onClose={() => setShowShare(false)} />
          )}
          {aiGenerateBuildingId && (
            <AIGenerateModal
              buildingId={aiGenerateBuildingId}
              buildingName={project.buildings?.find((b) => b.id === aiGenerateBuildingId)?.name}
              onClose={() => setAiGenerateBuildingId(null)}
              onComplete={() => {
                queryClient.invalidateQueries({ queryKey: ['project', id] });
                setAiGenerateBuildingId(null);
              }}
            />
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold text-primary-950">Project Details</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-primary-950/50">Status</dt>
                <dd className="mt-0.5 font-medium capitalize text-primary-950">{project.status}</dd>
              </div>
              <div>
                <dt className="text-primary-950/50">Created</dt>
                <dd className="mt-0.5 text-primary-950">
                  {new Date(project.created_at).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-primary-950/50">Last Updated</dt>
                <dd className="mt-0.5 text-primary-950">
                  {new Date(project.updated_at).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-primary-950/50">Buildings</dt>
                <dd className="mt-0.5 text-primary-950">{project.buildings?.length || 0}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
      <ImageLightbox />

      {/* Saved render lightbox */}
      {renderLightbox && (
        <div
          className="fixed inset-0 z-[250] flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={() => setRenderLightbox(null)}
        >
          <div className="relative max-h-[90vh] max-w-[90vw]" onClick={(e) => e.stopPropagation()}>
            <img
              src={resolveApiFileUrl(renderLightbox.image_url)}
              alt={renderLightbox.prompt || 'Saved render'}
              className="max-h-[85vh] max-w-full rounded-xl object-contain shadow-2xl"
            />
            <div className="absolute bottom-0 left-0 right-0 rounded-b-xl bg-gradient-to-t from-black/80 to-transparent px-5 py-4">
              {renderLightbox.prompt && (
                <p className="text-sm text-white/90 line-clamp-2">{renderLightbox.prompt}</p>
              )}
              <p className="mt-1 text-xs text-white/50">
                {new Date(renderLightbox.created_at).toLocaleDateString()}
                {renderLightbox.style && ` · ${renderLightbox.style}`}
              </p>
            </div>
            <div className="absolute top-3 right-3 flex gap-2">
              <a
                href={resolveApiFileUrl(renderLightbox.image_url)}
                download={`render-${renderLightbox.id}.png`}
                className="rounded-full bg-black/60 p-2 text-white/80 hover:bg-black/80 hover:text-white transition"
                title="Download"
              >
                <FileDown size={18} />
              </a>
              <button
                onClick={() => {
                  if (!id) return;
                  rendersApi.delete(id, renderLightbox.id).then(() => {
                    setSavedRenders((prev) => prev.filter((r) => r.id !== renderLightbox.id));
                    setRenderLightbox(null);
                    toast.success('Render deleted');
                  }).catch(() => toast.error('Failed to delete'));
                }}
                className="rounded-full bg-black/60 p-2 text-white/80 hover:bg-red-600 hover:text-white transition"
                title="Delete render"
              >
                <Trash2 size={18} />
              </button>
              <button
                onClick={() => setRenderLightbox(null)}
                className="rounded-full bg-black/60 p-2 text-white/80 hover:bg-black/80 hover:text-white transition"
              >
                <svg className="h-[18px] w-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Full-screen AI render result modal */}
      {showRenderModal && renderPreviews.length > 0 && (
        <RenderResultModal
          previews={renderPreviews}
          selectedIndex={renderModalSelectedIdx}
          onSelectPreview={handleModalSelectPreview}
          onClose={handleCloseRenderModal}
          isGeneratingFull={isGeneratingFull}
          fullResult={fullRenderResult}
          progressMessage={renderProgressMessage}
          projectId={project?.id}
          onSaved={() => {
            if (id) rendersApi.list(id).then(setSavedRenders).catch(() => {});
          }}
        />
      )}
    </div>
  );
}
