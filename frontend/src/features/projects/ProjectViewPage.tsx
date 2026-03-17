import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ArrowLeft, Eye, Upload, Building2, FileText, Plus, Loader2, CheckCircle, AlertCircle, Clock, Image, FileSpreadsheet, Trash2, Share2, MapPin, FileDown, Sparkles, RefreshCw } from 'lucide-react';
import { projectsApi, documentsApi, activityApi, buildingsApi } from '@/services/api';
import { AIGenerateModal } from '@/components/buildings/AIGenerateModal';
import { FileUpload } from '@/components/upload/FileUpload';
import { AddBuildingModal } from '@/components/buildings/AddBuildingModal';
import { ShareModal } from '@/components/sharing/ShareModal';
import { SitePlannerMap } from '@/components/viewer/SitePlannerMap';
import { SitePlannerToolbar } from '@/components/viewer/SitePlannerToolbar';
import { ZonePropertiesPanel } from '@/components/viewer/ZonePropertiesPanel';
import { WorkflowStepper } from '@/components/viewer/WorkflowStepper';
import { MassingOptionPicker } from '@/components/viewer/MassingOptionPicker';
import { massingOptionToGeoJSON } from '@/components/viewer/massingUtils';
import { useAIRender, AI_RENDER_STYLES } from '@/components/viewer/useAIRender';
import { collectArchetypeRenderInputs } from '@/components/viewer/collectArchetypeRenderInputs';
import { siteZonesApi } from '@/services/api';
import { useViewerStore } from '@/store';
import { useSiteZones } from '@/hooks/useSiteZones';
import { ImageLightbox } from '@/components/ui/ImageLightbox';
import type { Document } from '@/types';
import { WorkflowTabs, type WorkflowTab } from './WorkflowTabs';
import { EmbeddedBlockEditor } from '@/features/block-editor/EmbeddedBlockEditor';
import { MasterPlan2DPanel } from './MasterPlan2DPanel';

export function ProjectViewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showAddBuilding, setShowAddBuilding] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [aiGenerateBuildingId, setAiGenerateBuildingId] = useState<string | null>(null);
  const [workflowTab, setWorkflowTab] = useState<WorkflowTab>('master-plan');
  const queryClient = useQueryClient();
  const prevStatusMap = useRef<Record<string, string>>({});

  // Site planner store + zone CRUD
  const {
    setSitePlannerActive,
    setActiveSitePlannerTool,
    selectedZoneId,
    selectZone,
    masterPlan3D,
    siteMassing,
    setSiteMassing,
    setActiveMassingIndex,
    clearSiteMassing,
    workflowStep,
    setWorkflowStep,
    mapInstance,
  } = useViewerStore();

  const {
    siteZones,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  } = useSiteZones(id);

  const selectedZone = siteZones.find((z) => z.id === selectedZoneId) || null;

  // Workflow tab enablement
  const hasEditableZones = siteZones.some((z) =>
    (z.zone_type === 'building' || z.zone_type === 'residential' || z.zone_type === 'development_area')
  );
  const hasSiteGeometry = siteZones.some((z) => z.zone_type === 'site_boundary');
  const hasFinalizedLayout = siteZones.some((z) => (z.properties as any)?._saved_layout);
  const activeMasterPlan3D = masterPlan3D?.projectId === id ? masterPlan3D : null;
  const hasMasterPlan3DReady = Boolean(activeMasterPlan3D?.status === 'ready' && activeMasterPlan3D.packages.length > 0);

  // Activate site planner on mount, pre-select buildings tool
  useEffect(() => {
    setSitePlannerActive(true);
    setActiveSitePlannerTool('building');
    // Reset workflow state for this project
    setWorkflowStep(1);
    clearSiteMassing();
    return () => {
      setSitePlannerActive(false);
      setActiveSitePlannerTool(null);
      selectZone(null);
      // Clean up workflow state on unmount
      setWorkflowStep(1);
      clearSiteMassing();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setSitePlannerActive, setActiveSitePlannerTool, selectZone, id]);

  const handleZoneSelected = useCallback((zoneId: string | null) => {
    selectZone(zoneId);
  }, [selectZone]);

  const handleViewIn3D = useCallback(() => {
    navigate(`/projects/${id}/viewer`);
  }, [navigate, id]);

  const handleWalkThrough = useCallback(() => {
    navigate(`/projects/${id}/viewer`);
  }, [navigate, id]);

  // ── Massing generation ───────────────────────────────────────────────
  const [massingLoading, setMassingLoading] = useState(false);

  const handleGenerateMassing = useCallback(async () => {
    if (!id) return;
    setMassingLoading(true);
    try {
      const response = await siteZonesApi.generateSiteMassing(id);
      if (!response.options || response.options.length === 0) {
        toast.error('No massing options were generated — try adjusting zones');
        return;
      }
      setSiteMassing(id, response.options);
      setWorkflowStep(2);
      toast.success(`Generated ${response.options.length} massing options`);
    } catch (err: any) {
      console.error('Massing generation failed:', err);
      toast.error(err?.response?.data?.detail || 'Failed to generate massing options');
    } finally {
      setMassingLoading(false);
    }
  }, [id, setSiteMassing, setWorkflowStep]);

  const handleConfirmMassing = useCallback(() => {
    setWorkflowStep(3);
  }, [setWorkflowStep]);

  // Compute GeoJSON features for the active massing option
  const massingFeatures = useMemo(() => {
    if (!siteMassing || siteMassing.projectId !== id || siteMassing.options.length === 0) return undefined;
    const activeOption = siteMassing.options[siteMassing.activeIndex];
    if (!activeOption) return undefined;
    return massingOptionToGeoJSON(activeOption, siteZones);
  }, [siteMassing, siteZones, id]);

  // ── AI Render (Step 3) ──────────────────────────────────────────────
  const [selectedRenderStyle, setSelectedRenderStyle] = useState('modern-glass');
  const aiRender = useAIRender();
  // Destructure stable callbacks to avoid re-render loops in useCallback deps
  const { renderPreviews: aiRenderPreviews, renderFull: aiRenderFull } = aiRender;

  const handleRenderPreviews = useCallback(async () => {
    if (!mapInstance) {
      toast.error('Map not ready — please wait');
      return;
    }
    // Collect archetype prompts from zone selections
    const archetypeInputs = collectArchetypeRenderInputs(siteZones);
    // Only pass archetype prompts if zones actually have them — otherwise let
    // the style preset (selected via renderStyleId) drive the prompt alone.
    const archetypePrompt = archetypeInputs.positivePrompts.join(', ');
    const archetypeNegative = archetypeInputs.negativePrompts.join(', ');

    try {
      await aiRenderPreviews(mapInstance, {
        renderStyleId: selectedRenderStyle,
        archetypePrompt,
        archetypeNegative,
        referenceImageUrls: archetypeInputs.referenceImageUrls,
      });
    } catch (err: any) {
      console.error('AI render failed:', err);
      toast.error('AI render failed — check console');
    }
  }, [mapInstance, siteZones, aiRenderPreviews, selectedRenderStyle]);

  const handleRenderFull = useCallback(async (seed: number) => {
    if (!mapInstance) return;
    const archetypeInputs = collectArchetypeRenderInputs(siteZones);
    const archetypePrompt = archetypeInputs.positivePrompts.join(', ');
    const archetypeNegative = archetypeInputs.negativePrompts.join(', ');

    try {
      await aiRenderFull(mapInstance, {
        renderStyleId: selectedRenderStyle,
        archetypePrompt,
        archetypeNegative,
        referenceImageUrls: archetypeInputs.referenceImageUrls,
      }, seed);
    } catch (err: any) {
      console.error('AI render full failed:', err);
    }
  }, [mapInstance, siteZones, aiRenderFull, selectedRenderStyle]);

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      // Auto-refresh every 3 seconds while any document is processing or building is generating
      const data = query.state.data;
      if (!data) return false;
      const hasProcessing = data.documents?.some(
        (d: Document) => d.processing_status === 'pending' || d.processing_status === 'processing'
      );
      const hasGenerating = data.buildings?.some(
        (b: { generation_status?: string }) => b.generation_status === 'generating'
      );
      return (hasProcessing || hasGenerating) ? 3000 : false;
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

  const onUploadComplete = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['project', id] });
    queryClient.invalidateQueries({ queryKey: ['activity', id] });
  }, [queryClient, id]);

  const { data: activityLog } = useQuery({
    queryKey: ['activity', id],
    queryFn: () => activityApi.list(id!),
    enabled: !!id,
  });

  // Generation elapsed timer
  const generatingBuildingCount = useMemo(() => {
    if (!project?.buildings) return 0;
    return project.buildings.filter((b: { generation_status?: string }) => b.generation_status === 'generating').length;
  }, [project?.buildings]);

  const [genStartTime, setGenStartTime] = useState<number | null>(null);
  const [genElapsed, setGenElapsed] = useState(0);

  useEffect(() => {
    if (generatingBuildingCount > 0) {
      setGenStartTime((prev) => prev ?? Date.now());
    } else if (genStartTime) {
      setGenStartTime(null);
      setGenElapsed(0);
    }
  }, [generatingBuildingCount, genStartTime]);

  useEffect(() => {
    if (!genStartTime) return;
    const tick = setInterval(() => {
      setGenElapsed(Math.floor((Date.now() - genStartTime) / 1000));
    }, 1000);
    return () => clearInterval(tick);
  }, [genStartTime]);

  const processingDocCount = useMemo(() => {
    if (!project?.documents) return 0;
    return project.documents.filter(
      (d) => d.processing_status === 'pending' || d.processing_status === 'processing'
    ).length;
  }, [project?.documents]);

  if (isLoading) return <div className="text-center text-primary-950/50">Loading project...</div>;
  if (!project) return <div className="text-center text-primary-950/50">Project not found</div>;

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
          <Link to={`/projects/${id}/viewer`} className="btn-primary shrink-0">
            <Eye size={16} className="mr-2" />
            Open 3D Viewer
          </Link>
        </div>
      </div>
      <section className="relative left-1/2 mt-6 w-screen max-w-none -translate-x-1/2 overflow-hidden border-y border-primary-950/[0.08] shadow-card sm:rounded-xl sm:border">
        {/* Workflow Tabs */}
        <WorkflowTabs
          activeTab={workflowTab}
          onTabChange={setWorkflowTab}
          hasEditableZones={hasEditableZones}
          hasSiteGeometry={hasSiteGeometry}
          hasFinalizedLayout={hasFinalizedLayout}
          hasMasterPlan3DReady={hasMasterPlan3DReady}
        />

        {/* Tab 1: Master Plan */}
        {workflowTab === 'master-plan' && (
          <>
            {/* Workflow stepper bar */}
            <WorkflowStepper
              currentStep={workflowStep}
              onStepClick={(step) => {
                if (step < workflowStep) {
                  setWorkflowStep(step);
                  // Clear downstream state when stepping back
                  if (step <= 1) {
                    clearSiteMassing();
                    aiRender.reset();
                  }
                  if (step <= 2) {
                    aiRender.reset();
                  }
                }
              }}
            />

            <div className="relative h-[56vh] min-h-[430px] sm:h-[62vh] lg:h-[68vh]">
              <SitePlannerMap
                latitude={project.location?.latitude}
                longitude={project.location?.longitude}
                siteZones={siteZones}
                massingFeatures={massingFeatures}
                onZoneCreated={handleZoneCreated}
                onZoneUpdated={handleZoneUpdated}
                onZoneSelected={handleZoneSelected}
                onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
              />
              {/* Step 1: Zone properties panel */}
              {workflowStep === 1 && selectedZone && (
                <ZonePropertiesPanel
                  key={selectedZone.id}
                  zone={selectedZone}
                  onUpdate={(zoneId, data) => updateZone.mutate({ zoneId, data })}
                  onDelete={(zoneId) => deleteZone.mutate(zoneId)}
                  onClose={() => selectZone(null)}
                  onAIGenerate={(buildingId) => setAiGenerateBuildingId(buildingId)}
                  buildings={project.buildings}
                  allZones={siteZones}
                  onOpenBlockEditor={() => setWorkflowTab('block-editor')}
                />
              )}
              {/* Step 2: Massing option picker overlay */}
              {workflowStep === 2 && siteMassing && siteMassing.projectId === id && siteMassing.options.length > 0 && (
                <div className="absolute bottom-0 left-0 right-0 z-10 bg-gray-900/90 backdrop-blur-sm border-t border-gray-700">
                  <MassingOptionPicker
                    options={siteMassing.options}
                    activeIndex={siteMassing.activeIndex}
                    onSelect={setActiveMassingIndex}
                    onConfirm={handleConfirmMassing}
                  />
                </div>
              )}
              {/* Step 3: AI Render controls */}
              {workflowStep === 3 && (
                <div className="absolute bottom-0 left-0 right-0 z-10 bg-gray-900/90 backdrop-blur-sm border-t border-gray-700 p-4">
                  {/* Style selector */}
                  <div className="mb-3 flex items-center gap-3">
                    <label className="text-xs text-gray-400 whitespace-nowrap">Render Style:</label>
                    <select
                      value={selectedRenderStyle}
                      onChange={(e) => setSelectedRenderStyle(e.target.value)}
                      disabled={aiRender.isRendering}
                      className="flex-1 max-w-xs bg-gray-800 border border-gray-700 text-gray-200 text-xs rounded-lg px-3 py-1.5 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 disabled:opacity-50"
                    >
                      {AI_RENDER_STYLES.map((s) => (
                        <option key={s.id} value={s.id}>{s.label}</option>
                      ))}
                    </select>
                  </div>

                  {/* Render previews grid */}
                  {aiRender.previews.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs text-gray-400 mb-2">Select a preview to render at full quality:</p>
                      <div className="grid grid-cols-3 gap-2">
                        {aiRender.previews.map((preview, idx) => (
                          <button
                            key={idx}
                            onClick={() => {
                              aiRender.setSelectedPreviewIndex(idx);
                              if (preview.seed != null) handleRenderFull(preview.seed);
                            }}
                            className={`relative rounded-lg overflow-hidden border-2 transition-all ${
                              aiRender.selectedPreviewIndex === idx
                                ? 'border-purple-500 shadow-lg shadow-purple-500/30'
                                : 'border-gray-700 hover:border-gray-500'
                            }`}
                          >
                            <img
                              src={preview.imageUrl}
                              alt={`Preview ${idx + 1}`}
                              className="w-full aspect-video object-cover"
                            />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Full render result */}
                  {aiRender.result && (
                    <div className="mb-3 text-center">
                      <img
                        src={aiRender.result.imageUrl}
                        alt="Full AI Render"
                        className="max-h-48 mx-auto rounded-lg shadow-xl border border-gray-700"
                      />
                      <p className="text-xs text-green-400 mt-1">Full-quality render complete</p>
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex items-center justify-center gap-3">
                    {!aiRender.isRendering && aiRender.previews.length === 0 && (
                      <button
                        onClick={handleRenderPreviews}
                        className="px-6 py-2.5 bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold rounded-lg transition-colors"
                      >
                        <Sparkles size={14} className="inline mr-2" />
                        Generate AI Render
                      </button>
                    )}
                    {!aiRender.isRendering && aiRender.previews.length > 0 && (
                      <button
                        onClick={() => {
                          aiRender.reset();
                          handleRenderPreviews();
                        }}
                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5"
                      >
                        <RefreshCw size={12} />
                        Regenerate Previews
                      </button>
                    )}
                    {aiRender.isRendering && (
                      <div className="flex items-center gap-2 text-purple-400 text-sm">
                        <Loader2 size={14} className="animate-spin" />
                        Rendering... {aiRender.progress > 0 ? `${aiRender.progress}%` : ''}
                      </div>
                    )}
                    {aiRender.error && !aiRender.error.includes('VITE_FAL_KEY') && (
                      <p className="text-red-400 text-xs">{aiRender.error}</p>
                    )}
                    {!import.meta.env.VITE_FAL_KEY && (
                      <p className="text-red-400 text-xs">VITE_FAL_KEY is not set. Add it to your .env file.</p>
                    )}
                  </div>
                </div>
              )}
            </div>
            {/* Bottom toolbar with Generate button */}
            <div className="flex items-center justify-between gap-3 px-4 py-2 bg-gray-900 border-t border-gray-800">
              <div className="flex-1 min-w-0">
                <SitePlannerToolbar
                  onViewIn3D={handleViewIn3D}
                  onWalkThrough={handleWalkThrough}
                />
              </div>
              {workflowStep === 1 && (
                <button
                  onClick={handleGenerateMassing}
                  disabled={!hasEditableZones || massingLoading}
                  className={`
                    flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-semibold transition-all
                    ${hasEditableZones && !massingLoading
                      ? 'bg-blue-600 hover:bg-blue-500 text-white'
                      : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    }
                  `}
                >
                  {massingLoading ? (
                    <>
                      <Loader2 size={14} className="animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles size={14} />
                      Generate Options
                    </>
                  )}
                </button>
              )}
            </div>
          </>
        )}

        {/* Tab 2: Block Editor */}
        {workflowTab === 'block-editor' && id && (
          <EmbeddedBlockEditor
            projectId={id}
            zones={siteZones}
            onFinalized={() => setWorkflowTab('3d-viewer')}
          />
        )}

        {/* Tab 3: 2D Master Plan Generator */}
        {workflowTab === 'master-plan-2d' && id && (
          <MasterPlan2DPanel
            projectId={id}
            siteZones={siteZones}
            hasSiteGeometry={hasSiteGeometry}
          />
        )}

        {/* Tab 4: 3D Viewer placeholder */}
        {workflowTab === '3d-viewer' && (
          <div className="flex h-[500px] items-center justify-center rounded-b-xl bg-primary-950">
            <div className="max-w-xl px-6 text-center">
              {activeMasterPlan3D?.status === 'ready' ? (
                <>
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-200">3D Packages Ready</p>
                  <p className="mt-3 text-2xl font-semibold text-white">{activeMasterPlan3D.packages.length} geometry-locked scene packages are prepared.</p>
                  <p className="mt-3 text-sm text-neutral-300">
                    Source board: {activeMasterPlan3D.sourceOptionLabel || '2D master plan'} | {activeMasterPlan3D.selectedPerspective.replace(/_/g, ' ')} | {activeMasterPlan3D.lightingVariant.replace(/_/g, ' ')}
                  </p>
                  <p className="mt-2 text-sm text-neutral-400">
                    The downstream renderer handoff is ready, and the original 2D footprints remain authoritative.
                  </p>
                  {activeMasterPlan3D.globalStyleNotes && (
                    <p className="mt-3 text-sm text-neutral-300">Shared direction: {activeMasterPlan3D.globalStyleNotes}</p>
                  )}
                  {activeMasterPlan3D.packages.length > 0 && (
                    <div className="mt-5 grid gap-2 text-left sm:grid-cols-2">
                      {activeMasterPlan3D.packages.slice(0, 4).map((pkg) => (
                        <div key={pkg.scene_id} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
                          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-indigo-200">{pkg.zone_label}</p>
                          <p className="mt-1 text-sm font-medium text-white">{pkg.archetype_title}</p>
                          <p className="mt-1 text-xs text-neutral-300">
                            {pkg.height_m > 0 && pkg.floor_count > 0
                              ? `${pkg.height_m}m over ${pkg.floor_count} levels`
                              : pkg.zone_type.replace(/_/g, ' ')}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                  {activeMasterPlan3D.rendererAdapter?.notes && (
                    <p className="mt-3 text-xs text-neutral-400">{activeMasterPlan3D.rendererAdapter.notes}</p>
                  )}
                </>
              ) : activeMasterPlan3D?.status === 'generating' ? (
                <>
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-200">Preparing 3D</p>
                  <p className="mt-3 text-2xl font-semibold text-white">Your 2D master plan is being packaged for 3D rendering.</p>
                  <p className="mt-3 text-sm text-neutral-400">We are preserving footprint geometry, archetype metadata, and scene directives for the renderer handoff.</p>
                </>
              ) : (
                <p className="text-sm text-neutral-400">Your 3D environment is being generated</p>
              )}
              <button
                onClick={handleViewIn3D}
                className="mt-6 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-400 hover:to-purple-400"
              >
                Open 3D Viewer
              </button>
            </div>
          </div>
        )}
      </section>

      <div className="mt-8 grid gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Document Upload */}
          <section className="card">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-primary-950">
              <Upload size={20} />
              Upload Documents
            </h2>
            <div className="mt-4">
              <FileUpload projectId={project.id} onUploadComplete={onUploadComplete} />
            </div>
          </section>

          {/* Documents List */}
          {project.documents && project.documents.length > 0 && (
            <section className="card">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-primary-950">
                  <FileText size={20} />
                  Documents
                  {processingDocCount > 0 && (
                    <span className="ml-2 flex items-center gap-1 rounded-full bg-amber-500/15 px-2 py-0.5 text-xs text-amber-400">
                      <Loader2 size={12} className="animate-spin" />
                      {processingDocCount} processing
                    </span>
                  )}
                </h2>
              </div>
              <div className="mt-4 space-y-2">
                {project.documents.map((doc) => (
                  <DocumentRow key={doc.id} document={doc} onDelete={onUploadComplete} />
                ))}
              </div>
            </section>
          )}

          {/* Buildings */}
          <section className="card">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-primary-950">
                <Building2 size={20} />
                Buildings
              </h2>
              <button
                onClick={() => setShowAddBuilding(true)}
                className="flex items-center gap-1 rounded-lg bg-primary-500/15 px-3 py-1.5 text-sm font-medium text-primary-400 hover:bg-primary-500/25"
              >
                <Plus size={16} />
                Add Building
              </button>
            </div>
            {project.buildings?.length ? (
              <div className="mt-4 space-y-3">
                {project.buildings.map((b) => (
                  <div key={b.id} className="flex items-center justify-between rounded-lg border border-primary-950/[0.08] p-4">
                    <div>
                      <p className="font-medium text-primary-950">{b.name || 'Unnamed Building'}</p>
                      <p className="text-sm text-primary-950/50">
                        {b.floor_count && `${b.floor_count} floors`}
                        {b.height_meters && ` | ${b.height_meters}m tall`}
                        {b.roof_type && ` | ${b.roof_type} roof`}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {b.model_url ? (
                        <span className="badge bg-emerald-500/15 text-emerald-400">
                          3D Ready
                        </span>
                      ) : b.generation_status === 'generating' ? (
                        <span className="flex items-center gap-1 badge bg-primary-500/15 text-primary-400">
                          <Loader2 size={10} className="animate-spin" />
                          Generating...
                          {genElapsed > 0 && (
                            <span className="tabular-nums text-primary-500">
                              {Math.floor(genElapsed / 60)}:{(genElapsed % 60).toString().padStart(2, '0')}
                            </span>
                          )}
                        </span>
                      ) : b.generation_status === 'failed' ? (
                        <span className="badge bg-red-500/15 text-red-600">
                          Failed
                        </span>
                      ) : (
                        <button
                          onClick={() => setAiGenerateBuildingId(b.id)}
                          className="flex items-center gap-1 rounded-full bg-purple-500/15 px-2.5 py-0.5 text-xs font-medium text-purple-400 hover:bg-purple-500/25"
                          title="Generate 3D model with AI"
                        >
                          <Sparkles size={10} />
                          Generate 3D
                        </button>
                      )}
                      <button
                        onClick={() => {
                          if (confirm(`Delete "${b.name || 'this building'}"? This cannot be undone.`)) {
                            buildingsApi.delete(b.id).then(() => {
                              queryClient.invalidateQueries({ queryKey: ['project', id] });
                              toast.success('Building deleted');
                            }).catch(() => {
                              toast.error('Failed to delete building');
                            });
                          }
                        }}
                        className="rounded-md p-1.5 text-primary-950/40 hover:bg-red-50 hover:text-red-600"
                        title="Delete building"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-primary-950/50">
                No buildings yet. Upload documents or add buildings manually.
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
              <div>
                <dt className="text-primary-950/50">Documents</dt>
                <dd className="mt-0.5 text-primary-950">{project.documents?.length || 0}</dd>
              </div>
            </dl>
          </div>

          {/* Activity Feed */}
          {activityLog && activityLog.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-primary-950">Recent Activity</h3>
              <ul className="mt-3 space-y-2">
                {activityLog.slice(0, 10).map((entry) => {
                  const actionLabels: Record<string, string> = {
                    document_uploaded: 'uploaded a document',
                    building_created: 'added a building',
                    annotation_created: 'added an annotation',
                    building_updated: 'updated a building',
                  };
                  const label = actionLabels[entry.action] || entry.action.replace(/_/g, ' ');
                  const name = entry.user_name || entry.user_email?.split('@')[0] || 'System';
                  const timeAgo = formatTimeAgo(entry.created_at);
                  return (
                    <li key={entry.id} className="flex items-start gap-2 text-xs text-primary-950/50">
                      <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary-400" />
                      <span>
                        <span className="font-medium text-neutral-100">{name}</span>{' '}
                        {label}
                        {entry.details?.filename && (
                          <span className="text-primary-950/50"> ({entry.details.filename as string})</span>
                        )}
                        {entry.details?.name && (
                          <span className="text-primary-950/50"> ({entry.details.name as string})</span>
                        )}
                        <span className="ml-1 text-primary-950/50">{timeAgo}</span>
                      </span>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      </div>
      <ImageLightbox />
    </div>
  );
}

function formatTimeAgo(dateStr: string): string {
  const ms = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(ms / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function DocumentRow({ document: doc, onDelete }: { document: Document; onDelete: () => void }) {
  const [deleting, setDeleting] = useState(false);

  const statusConfig = {
    pending: { icon: <Clock size={14} />, color: 'text-amber-400 bg-amber-500/10', label: 'Pending' },
    processing: { icon: <Loader2 size={14} className="animate-spin" />, color: 'text-primary-400 bg-primary-500/15', label: 'Processing' },
    completed: { icon: <CheckCircle size={14} />, color: 'text-emerald-400 bg-emerald-500/15', label: 'Completed' },
    failed: { icon: <AlertCircle size={14} />, color: 'text-red-600 bg-red-50', label: 'Failed' },
  };

  const status = statusConfig[doc.processing_status] || statusConfig.pending;

  const getFileIcon = () => {
    const ext = doc.file_type.toLowerCase();
    if (ext === 'pdf') return <FileText size={16} className="text-red-500" />;
    if (['jpg', 'jpeg', 'png', 'tiff'].includes(ext)) return <Image size={16} className="text-green-500" />;
    if (['csv', 'xlsx'].includes(ext)) return <FileSpreadsheet size={16} className="text-primary-500" />;
    return <FileText size={16} className="text-primary-950/40" />;
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${doc.filename}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await documentsApi.delete(doc.id);
      toast.success(`"${doc.filename}" deleted`);
      onDelete();
    } catch {
      toast.error('Failed to delete document');
      setDeleting(false);
    }
  };

  const isProcessing = doc.processing_status === 'processing' || doc.processing_status === 'pending';

  return (
    <div className="group rounded-lg border border-primary-950/[0.08] bg-white">
      <div className="flex items-center gap-3 px-4 py-3">
        {getFileIcon()}
        <div className="flex-1 min-w-0">
          <p className="truncate text-sm font-medium text-primary-950/60">{doc.filename}</p>
          <p className="text-xs text-primary-950/50">
            {formatSize(doc.file_size_bytes)} | {doc.file_type.toUpperCase()}
            {doc.processed_at && ` | Processed ${new Date(doc.processed_at).toLocaleDateString()}`}
          </p>
        </div>
        <span className={`flex items-center gap-1 badge ${status.color}`}>
          {status.icon}
          {status.label}
        </span>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="ml-1 rounded-md p-1 text-primary-950/40 opacity-100 transition-opacity hover:bg-red-50 hover:text-red-500 sm:opacity-0 sm:group-hover:opacity-100 disabled:opacity-50"
          title="Delete document"
        >
          {deleting ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
        </button>
      </div>
      {isProcessing && (
        <div className="px-4 pb-3">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-primary-950/[0.04]">
            <div
              className="h-full rounded-full bg-gradient-to-r from-primary-400 via-primary-500 to-primary-400 animate-[shimmer_1.5s_ease-in-out_infinite]"
              style={{
                width: doc.processing_status === 'pending' ? '30%' : '70%',
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s ease-in-out infinite',
              }}
            />
          </div>
          <p className="mt-1 text-[10px] text-primary-950/50">
            {doc.processing_status === 'pending' ? 'Queued for processing...' : 'Extracting data and generating 3D models...'}
          </p>
        </div>
      )}
    </div>
  );
}











