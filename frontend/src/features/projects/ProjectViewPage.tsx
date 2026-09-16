import { canonicalDrawing } from '@/features/pickPlace/canonicalCatalogue';
import { canonicalBuildingAsset } from '@/features/pickPlace/canonicalBuildingPlacement';
import { streetFacingDegrees } from '@/features/pickPlace/streetFacing';
import { catalogueZoneForBuilding } from '@/features/pickPlace/catalogueDeletion';
import { lazy, Suspense, useState, useCallback, useMemo, useRef, useEffect, type PointerEvent as ReactPointerEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ArrowLeft, Blocks, Camera, CheckCircle, FileDown, MapPin, Share2, Sparkles, Trash2, Video, Wand2, X } from 'lucide-react';
import { buildingsApi, projectsApi, rendersApi, resolveApiFileUrl, siteZonesApi, videoRenderApi } from '@/services/api';
import type { SavedRender, SiteZone } from '@/types';
import { AIGenerateModal } from '@/components/buildings/AIGenerateModal';
import { LegoAssemblyPreview } from '@/features/legoAssembly/LegoAssemblyPreview';
import { LegoBuilderPanel } from '@/features/legoAssembly/LegoBuilderPanel';
import { AddBuildingModal } from '@/components/buildings/AddBuildingModal';
import { ShareModal } from '@/components/sharing/ShareModal';
import { SitePlannerToolbar } from '@/components/viewer/SitePlannerToolbar';
import { PlacementPalette } from '@/features/pickPlace/PlacementPalette';
import { ReshapePanel } from '@/features/pickPlace/ReshapePanel';
import { parkOutlineProblem } from '@/features/pickPlace/parkOutline';
import { StreetRoutePanel } from '@/features/pickPlace/StreetRoutePanel';
import { publicRoadConnectionFits } from '@/features/pickPlace/publicRoadConnection';
import { ConnectionEditor } from '@/features/pickPlace/ConnectionEditor';
import { TerraceEditor } from '@/features/pickPlace/TerraceEditor';
import { saveAutomaticParkGround } from '@/features/pickPlace/saveAutomaticParkGround';
import { TerraceSummary } from '@/features/pickPlace/TerraceSummary';
import { CALGARY_LOCAL_PLACEMENT, isFixedSectionStreet, streetRouteProblem, streetSectionWidth } from '@/features/pickPlace/streetPlacement';
import { assetForZone, placeAsset, placementProperties, type PlaceAssetId } from '@/features/pickPlace/catalogue';
import { placementProblem, rectangleAt } from '@/features/pickPlace/geometry';
import { useAutomatic3D } from '@/features/pickPlace/useAutomatic3D';
import type { PlacementDraft } from '@/features/pickPlace/GlobePlacementPreview';
import { HistoryPanel } from '@/components/viewer/HistoryPanel';
import { GlobeAIRenderPanel } from '@/components/viewer/globe/GlobeAIRenderPanel';
import { VideoGeneratePanel, type VideoAttempt } from '@/components/viewer/VideoGeneratePanel';
import { captureCompleteVideoFrame, type VideoCaptureScene } from '@/components/viewer/videoCaptureInventory';
import type { VideoRouteCaptureRequest, VideoRouteCaptureResult } from '@/components/viewer/videoRouteControls';
import { nearestAspectRatio, useGlobeAIRender } from '@/components/viewer/globe/useGlobeAIRender';
import type { StreetCaptureResult } from '@/components/viewer/useStreetViewRender';
import { useGlobeCamera } from '@/components/viewer/globe/useGlobeCamera';
import { ZonePropertiesPanel, useZonePropertiesReload } from '@/components/viewer/ZonePropertiesPanel';
import { AIRenderPanel } from '@/components/viewer/AIRenderPanel';
import { RenderResultModal } from '@/components/viewer/RenderResultModal';
import { RenderEditModal } from '@/components/viewer/RenderEditModal';
import { ZoneLegend } from '@/components/viewer/ZoneLegend';
import { StreetViewPanel } from '@/components/viewer/StreetViewPanel';
import { WorkflowStepper } from '@/components/viewer/WorkflowStepper';
import { StudioControls, StudioDialog, StudioSaveStatus } from './StudioControls';
import { ReadOnlyProject } from './ReadOnlyProject';
import { StudentWorkflowNav, StudentStepPanel, type StudentStep } from './StudentWorkflow';
import { StudentPlanningReport } from '@/features/studentReports/StudentPlanningReport';
import { useReferenceLayers } from '@/features/referenceLayers/useReferenceLayers';
import { CalgaryContextButton } from '@/features/referenceLayers/CalgaryContextButton';
import { existingTransport } from '@/features/referenceLayers/existingTransport';
import { ReferenceLayersPanel } from '@/features/referenceLayers/ReferenceLayersPanel';
import { SiteElevation } from '@/features/referenceLayers/SiteElevation';
import { ShapefileImportButton } from './ShapefileImportButton';
import { LayersPanel } from './LayersPanel';
import { OnboardingTour } from '@/components/viewer/OnboardingTour';
import type { AIRenderResult } from '@/components/viewer/useAIRender';
import { useViewerStore } from '@/store';
import { useSiteZones } from '@/hooks/useSiteZones';
import { useUndoRedoKeyboard } from '@/hooks/useUndoRedoKeyboard';
import { rebufferRoadOnUpdate } from '@/utils/roadGeometry';
import { ImageLightbox } from '@/components/ui/ImageLightbox';
import { getRenderImageKey, saveRenderedImage } from '@/utils/renderPersistence';
import { savedRenderIsSource, savedRenderNeedsReview, savedRenderNotice } from '@/utils/renderPresentation';
import { isTextEntryTarget } from '@/utils/domEvents';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { authoredCameraGround } from '@/components/viewer/globe/authoredCameraGround';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import {
  deriveCityPromptWorkflow,
  type CityPromptWorkflowStep,
} from '@/features/workflow/cityPromptWorkflow';
import { withModeledBuildingRenderZones } from '@/components/viewer/globe/modelRenderZones';
import { filterBuildingsForVisibleCommunity3DScope } from '@/features/community3d/community3d';
import type {
  Direct3DCaptureBundle,
  Direct3DCaptureOptions,
} from '@/components/viewer/globe/direct3dCapture';

const GLOBE_RENDER_PANEL_WIDTH = 704;
const PLAN_LAYER_PREFIX = 'Plan — ';
const SitePlannerMap = lazy(() => import('@/components/viewer/SitePlannerMap').then((module) => ({ default: module.SitePlannerMap })));
const GlobeSitePlannerMap = lazy(() => import('@/components/viewer/globe/GlobeSitePlannerMap').then((module) => ({ default: module.GlobeSitePlannerMap })));

function MapLoadingFallback({ mode }: { mode: '2D' | '3D' }) {
  return (
    <div className="flex h-full w-full items-center justify-center bg-slate-950 text-sm font-semibold text-white" role="status">
      Loading {mode} site…
    </div>
  );
}

function planLayerStorageKey(projectId: string): string {
  return `cityprompt:active-plan-layer:${projectId}`;
}

export function ProjectViewPage() {
  const { id } = useParams<{ id: string }>();
  const [placementDraft, setPlacementDraft] = useState<PlacementDraft | null>(null);
  const [advancedZoneId, setAdvancedZoneId] = useState<string | null>(null);
  const placementPending = useRef(false);
  const [showAddBuilding, setShowAddBuilding] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [showReferenceLayers, setShowReferenceLayers] = useState(false);
  const [showPlanningReport, setShowPlanningReport] = useState(false);
  const closePlanningReport = useCallback(() => setShowPlanningReport(false), []);
  const references = useReferenceLayers(id);
  const transportContext = useMemo(() => existingTransport(references.layers), [references.layers]);
  const [aiGenerateBuildingId, setAiGenerateBuildingId] = useState<string | null>(null);
  const [legoZone, setLegoZone] = useState<SiteZone | null>(null);
  const [showLegoBuilder, setShowLegoBuilder] = useState(false);
  const [isPreparingGenerate3D, setIsPreparingGenerate3D] = useState(false);
  const [generate3DZones, setGenerate3DZones] = useState<SiteZone[] | null>(null);
  const [savedRenders, setSavedRenders] = useState<SavedRender[]>([]);
  const [savedVideos, setSavedVideos] = useState<VideoAttempt[]>([]);
  const [renderLightbox, setRenderLightbox] = useState<SavedRender | null>(null);
  const [videoLightbox, setVideoLightbox] = useState<VideoAttempt | null>(null);
  const [renderEditTarget, setRenderEditTarget] = useState<SavedRender | null>(null);
  const [showProjectRenders, setShowProjectRenders] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [showCatalogue, setShowCatalogue] = useState(false);
  const [studentStep, setStudentStep] = useState<StudentStep | null>(null);
  const [showGlobeRender, setShowGlobeRender] = useState(false);
  const [showVideoRender, setShowVideoRender] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [measureActive, setMeasureActive] = useState(false);
  const [aiPanelLightboxOpen, setAiPanelLightboxOpen] = useState(false);
  const [globeRenderPosition, setGlobeRenderPosition] = useState<{ x: number; y: number } | null>(null);
  const [isDraggingGlobeRender, setIsDraggingGlobeRender] = useState(false);
  const [globeRefs, setGlobeRefs] = useState<{
    canvas: HTMLCanvasElement;
    camera: any;
    terrainHeight: number;
    isSettled?: boolean;
    waitForTilesSettled?: () => Promise<boolean>;
    setBuildingModelsVisible?: (visible: boolean) => void;
    captureDirect3D?: (options?: {
      skipTileWait?: boolean;
      includeGeometryPasses?: boolean;
      maxLongEdge?: number;
    }) => Promise<Direct3DCaptureBundle>;
    withStreetCaptureScene?: <T>(fn: (kind: 'model3d' | 'context3d') => Promise<T>) => Promise<T>;
    captureStreetDirect3D?: (options?: Direct3DCaptureOptions) => Promise<Direct3DCaptureBundle | null>;
    captureVideoRouteControls?: (request: VideoRouteCaptureRequest) => Promise<VideoRouteCaptureResult>;
  } | null>(null);
  // Buildings whose generated GLB is currently placed on the globe — the
  // render panel keys "render with 3D models" behavior off this set.
  const [modeledBuildingIds, setModeledBuildingIds] = useState<Set<string>>(() => new Set());
  const videoCaptureSceneRef = useRef<VideoCaptureScene>({ projectId: id, zones: [], buildings: [] });
  const queryClient = useQueryClient();
  const prevStatusMap = useRef<Record<string, string>>({});
  const globeRenderDragRef = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(null);

  // Globe street view capture
  const { captureStreetView } = useGlobeAIRender();
  const { flyToStreetLevel, restoreAerialView, saveCameraState } = useGlobeCamera();

  const handleGlobeStreetCapture = useCallback(async (): Promise<StreetCaptureResult | null> => {
    if (!globeRefs?.canvas || !globeRefs?.camera) return null;
    const pegman = useViewerStore.getState().streetViewPegman;
    if (!pegman?.position) return null;
    const [lng, lat] = pegman.position;
    const runCapture = async (kind: 'model3d' | 'context3d'): Promise<StreetCaptureResult | null> => {
      // Strip a data: URL prefix — the render API expects raw base64.
      const rawB64 = (value: string) => (value.includes(',') ? value.split(',')[1] : value);
      // With authored models in scene, grab the full Direct 3D pass stack
      // while the camera is parked at street level: clean off-screen beauty
      // (no editor affordances by construction) + the class-ID semantic frame
      // that anchors depth ordering. Falls back to a plain screenshot.
      const captureState: { bundle: Direct3DCaptureBundle | null } = { bundle: null };
      const captureFrame = kind === 'model3d' && globeRefs.captureStreetDirect3D
        ? async () => {
          captureState.bundle = await globeRefs.captureStreetDirect3D!();
          return captureState.bundle ? rawB64(captureState.bundle.beautyImageBase64) : null;
        }
        : undefined;
      const imageBase64 = await captureStreetView(
        globeRefs.canvas, globeRefs.camera,
        lat, lng, pegman.angle,
        authoredCameraGround(videoCaptureSceneRef.current.zones, lng, lat, pegman.terrainHeight ?? globeRefs.terrainHeight),
        flyToStreetLevel, restoreAerialView, saveCameraState,
        globeRefs.waitForTilesSettled,
        captureFrame,
      );
      if (!imageBase64) return null;
      const captured = captureState.bundle;
      return {
        imageBase64,
        kind,
        aspectRatio: captured
          ? nearestAspectRatio(captured.width, captured.height)
          : nearestAspectRatio(globeRefs.canvas.width, globeRefs.canvas.height),
        semanticBase64: captured ? rawB64(captured.classIdImageBase64) : undefined,
        direct3d: captured ?? undefined,
      };
    };
    // Scene hygiene (hide pegman marker; models vs overlays per kind) lives in
    // the globe component. Without it, fall back to a plain existing-context
    // capture — same behavior street view had before 3D models existed.
    return globeRefs.withStreetCaptureScene
      ? globeRefs.withStreetCaptureScene(runCapture)
      : runCapture('context3d');
  }, [globeRefs, captureStreetView, flyToStreetLevel, restoreAerialView, saveCameraState]);

  const captureVideoAerialFrame = useCallback(async (): Promise<string | null> => {
    const capture = globeRefs?.captureDirect3D;
    if (!capture) throw new Error('Wait for your 3D scene to finish loading, then capture your video again.');
    return captureCompleteVideoFrame(() => capture({ skipTileWait: true }), () => videoCaptureSceneRef.current);
  }, [globeRefs]);

  const captureVideoRouteControls = useCallback(async (
    request: VideoRouteCaptureRequest,
  ): Promise<VideoRouteCaptureResult> => {
    if (!globeRefs?.captureVideoRouteControls) {
      throw new Error('Route control capture is unavailable until the 3D globe has finished starting.');
    }
    return globeRefs.captureVideoRouteControls(request);
  }, [globeRefs]);

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
    activeSitePlannerTool, activeToolProperties,
    lightboxImageUrl,
  } = useViewerStore();

  const {
    siteZones,
    siteZonesLoading,
    siteZonesError, reloadZones, pendingDrafts, retryDraft, isSaving, draftsPersistOnDevice, discardableDrafts, discardDraft, saveError,
    updateZone,
    createZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  } = useSiteZones(id);
  const { savedVersionReload, reloadSavedVersion } = useZonePropertiesReload(id, selectedZoneId, reloadZones);

  const initializedSiteToolProjectRef = useRef<string | null>(null);

  const selectedZone = siteZones.find((z) => z.id === selectedZoneId) || null;
  const [connectionZoneId, setConnectionZoneId] = useState<string | null>(null);
  const connectionZone = siteZones.find(zone=>zone.id===connectionZoneId);
  const [terraceZoneId,setTerraceZoneId]=useState<string|null>(null);
  const terraceZone=siteZones.find(zone=>zone.id===terraceZoneId);
  const cancelPlacement = useCallback(() => setPlacementDraft(null), []);
  const pickObject = (assetId: PlaceAssetId, width?: number, depth?: number, degrees = 0) => {
    const asset = placeAsset(assetId);
    setActiveSitePlannerTool(null); selectZone(null); setMeasureActive(false);
    useViewerStore.getState().setStreetViewActive(false);
    setPlacementDraft({ assetId, width: width ?? asset.width, depth: depth ?? asset.depth, degrees,
      faceStreet: asset.zoneType === 'building' && width === undefined });
  };
  useEffect(() => {
    if (!placementDraft) return;
    const cancel = (event: KeyboardEvent) => { if(event.key === 'Escape' && !isTextEntryTarget(event.target)) cancelPlacement(); };
    window.addEventListener('keydown', cancel);
    return () => window.removeEventListener('keydown', cancel);
  }, [placementDraft, cancelPlacement]);
  useEffect(() => { setPlacementDraft(null); setAdvancedZoneId(null); }, [id]);
  const placeObject = async (point: [number, number], height: number) => {
    if (!placementDraft || placementDraft.inputError || placementPending.current || isSaving) return;
    const degrees = placementDraft.faceStreet ? streetFacingDegrees(point, siteZones, placementDraft.degrees) : placementDraft.degrees;
    const coordinates = rectangleAt(point, placementDraft.width, placementDraft.depth, degrees);
    const problem = placementProblem(coordinates, siteZones, getActiveSiteBoundary(siteZones));
    if(problem) { toast.error(problem, { position: 'top-center' }); return; }
    placementPending.current = true;
    try {
      const zone = await createZone.mutateAsync({ coordinates, zone_type: placeAsset(placementDraft.assetId).zoneType,
        properties: placementProperties(placeAsset(placementDraft.assetId), height) });
      setPlacementDraft(null); setAdvancedZoneId(null); selectZone(zone.id);
    } catch {
      // Retrying uses the saved draft's idempotency key, not a second placement.
      setPlacementDraft(null);
    }
    finally { placementPending.current = false; }
  };
  const reshapeObject = (zoneId: string, coordinates: number[][]): boolean => {
    const zone = siteZones.find(item => item.id === zoneId);
    if (zone && (assetForZone(zone) || isFixedSectionStreet(zone))) {
      if (isSaving) { toast.error('Wait for this edit to save.'); return false; }
      const problem = (zone.zone_type === 'green_space' ? parkOutlineProblem(coordinates)
        : assetForZone(zone)?.reshapeMode === 'authored_footprint' ? parkOutlineProblem(coordinates)?.replace(/park/g, 'building') : null)
        ?? (isFixedSectionStreet(zone) ? streetRouteProblem(coordinates, streetSectionWidth(zone)) : null)
        ?? placementProblem(coordinates, siteZones,
          publicRoadConnectionFits(zone, coordinates, getActiveSiteBoundary(siteZones)) ? null : getActiveSiteBoundary(siteZones), zoneId);
      if(problem) { toast.error(problem, { position: 'top-center' }); return false; }
    }
    handleZoneUpdated(zoneId, coordinates);
    return true;
  };

  // --- Imported shapefile "layers" (zones grouped by properties._imported_from) ---
  const [hiddenLayers, setHiddenLayers] = useState<Set<string>>(new Set());
  const [deletingLayer, setDeletingLayer] = useState<string | null>(null);

  const toggleLayer = useCallback((name: string) => {
    setHiddenLayers((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  }, []);

  const visibleZones = useMemo(() => {
    if (hiddenLayers.size === 0) return siteZones;
    return siteZones.filter((z) => {
      const src = z.properties?._imported_from;
      return !(typeof src === 'string' && hiddenLayers.has(src));
    });
  }, [siteZones, hiddenLayers]);

  const visiblePlanLayers = useMemo(() => [...new Set(visibleZones.flatMap((zone) => {
    const source = zone.properties?._imported_from;
    return typeof source === 'string' && source.startsWith(PLAN_LAYER_PREFIX) ? [source] : [];
  }))], [visibleZones]);

  // Multiple Master Planner alternatives are comparison layers, not one
  // physical community. Restore the last active alternative after refresh;
  // on an older project with no saved choice, select the most recently drawn
  // layer. Users can still choose All for 2D comparison, but compilation below
  // will require them to return to one physical scenario.
  const initializedPlanVisibilityProjectRef = useRef<string | null>(null);
  useEffect(() => {
    if (!id || siteZones.length === 0 || initializedPlanVisibilityProjectRef.current === id) return;
    const grouped = new Map<string, SiteZone[]>();
    for (const zone of siteZones) {
      const source = zone.properties?._imported_from;
      if (typeof source !== 'string' || !source.startsWith(PLAN_LAYER_PREFIX)) continue;
      grouped.set(source, [...(grouped.get(source) ?? []), zone]);
    }
    if (grouped.size < 2) {
      initializedPlanVisibilityProjectRef.current = id;
      return;
    }
    const stored = window.localStorage.getItem(planLayerStorageKey(id));
    const active = stored && grouped.has(stored)
      ? stored
      : [...grouped.entries()].sort(([, left], [, right]) => {
        const newest = (zones: SiteZone[]) => Math.max(...zones.map((zone) => (
          Date.parse(zone.updated_at || zone.created_at) || 0
        )));
        return newest(right) - newest(left);
      })[0][0];
    initializedPlanVisibilityProjectRef.current = id;
    window.localStorage.setItem(planLayerStorageKey(id), active);
    setHiddenLayers((previous) => {
      const next = new Set(previous);
      for (const layer of grouped.keys()) {
        if (layer === active) next.delete(layer);
        else next.add(layer);
      }
      return next;
    });
  }, [id, siteZones]);

  useEffect(() => {
    if (!id || initializedPlanVisibilityProjectRef.current !== id || visiblePlanLayers.length !== 1) return;
    window.localStorage.setItem(planLayerStorageKey(id), visiblePlanLayers[0]);
  }, [id, visiblePlanLayers]);

  // Height-framework layers are reference overlays (LAP-style storey bands
  // covering whole blocks) — visible by default they bury the actual plan
  // under one giant polygon. Hide each ONCE on first sight; a user re-show
  // from the Layers panel sticks because we never auto-hide the same layer twice.
  const autoHiddenFrameworksRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    const frameworks = siteZones
      .map((z) => z.properties?._imported_from)
      .filter((src): src is string => typeof src === 'string' && src.startsWith('Height framework — '));
    const fresh = frameworks.filter((name) => !autoHiddenFrameworksRef.current.has(name));
    if (fresh.length === 0) return;
    fresh.forEach((name) => autoHiddenFrameworksRef.current.add(name));
    setHiddenLayers((prev) => {
      const next = new Set(prev);
      fresh.forEach((name) => next.add(name));
      return next;
    });
  }, [siteZones]);

  // Solo one scenario's plan on the globe (dispatched by SiteIntelligencePanel,
  // which sits two components down inside ZonePropertiesPanel). Only plan and
  // height-framework layers are touched; shapefile-layer hiding is preserved.
  useEffect(() => {
    // Solo manages ONLY drawn plan layers. Height-framework overlays are owned
    // by the auto-hide effect above and must stay hidden — including through
    // "All" (a null label). Treating frameworks as "planish" here previously
    // stripped them out of hiddenLayers on every solo/All, and the auto-hide
    // effect (one-shot per name) never re-hid them, flooding the plan with
    // giant storey-band polygons.
    const isPlanLayer = (name: string) => name.startsWith(PLAN_LAYER_PREFIX);
    const onSolo = (event: Event) => {
      const label = (event as CustomEvent<{ label?: string | null }>).detail?.label;
      if (id) {
        if (label) window.localStorage.setItem(planLayerStorageKey(id), `${PLAN_LAYER_PREFIX}${label}`);
        else window.localStorage.removeItem(planLayerStorageKey(id));
      }
      setHiddenLayers((prev) => {
        const next = new Set([...prev].filter((n) => !isPlanLayer(n)));
        if (!label) return next; // "All" — show every plan (frameworks untouched)
        for (const zone of siteZones) {
          const src = zone.properties?._imported_from;
          if (typeof src === 'string' && isPlanLayer(src) && src !== `${PLAN_LAYER_PREFIX}${label}`) {
            next.add(src);
          }
        }
        return next;
      });
    };
    window.addEventListener('cityprompt:solo-plan-layer', onSolo);
    return () => window.removeEventListener('cityprompt:solo-plan-layer', onSolo);
  }, [id, siteZones]);

  const deleteLayer = useCallback(async (name: string) => {
    const zones = siteZones.filter((z) => {
      const src = z.properties?._imported_from;
      return typeof src === 'string' && src === name;
    });
    if (zones.length === 0) return;
    setDeletingLayer(name);
    const toastId = toast.loading(`Deleting layer "${name}"…`);
    try {
      for (const z of zones) await siteZonesApi.delete(z.id);
      await queryClient.invalidateQueries({ queryKey: ['site-zones', id] });
      setHiddenLayers((prev) => {
        const next = new Set(prev);
        next.delete(name);
        return next;
      });
      toast.success(
        `Deleted "${name}" (${zones.length} feature${zones.length === 1 ? '' : 's'})`,
        { id: toastId },
      );
    } catch (e) {
      toast.error(`Failed to delete layer: ${(e as Error).message}`, { id: toastId });
    } finally {
      setDeletingLayer(null);
    }
  }, [siteZones, queryClient, id]);

  const cityPromptWorkflow = useMemo(
    () => deriveCityPromptWorkflow(
      visibleZones,
      savedRenders.length > 0 || savedVideos.length > 0,
    ),
    [savedRenders.length, savedVideos.length, visibleZones],
  );

  useEffect(() => {
    if (!siteZonesLoading && workflowStep === 2 && !cityPromptWorkflow.canRender) {
      setWorkflowStep(1);
    }
  }, [cityPromptWorkflow.canRender, setWorkflowStep, siteZonesLoading, workflowStep]);

  // A project opens in selection mode. Late responses from a previous project
  // must not replace this project's media tray after navigation.
  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setSavedRenders([]); setSavedVideos([]); setRenderLightbox(null); setVideoLightbox(null);
    rendersApi.list(id).then((items) => { if (!cancelled) setSavedRenders(items); }).catch(() => {});
    videoRenderApi.list(id).then((result) => {
      const state = result as { attempts?: VideoAttempt[] };
      if (!cancelled) setSavedVideos((state.attempts ?? []).filter((attempt) => attempt.status === 'complete' && attempt.video_url));
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [id]);

  useEffect(() => {
    setSitePlannerActive(true);
    setActiveSitePlannerTool(null);
    setWorkflowStep(1);
    return () => {
      setSitePlannerActive(false);
      setActiveSitePlannerTool(null);
      selectZone(null);
    };
  }, [setSitePlannerActive, setActiveSitePlannerTool, selectZone, setWorkflowStep, id]);

  useEffect(() => {
    if (!id || siteZonesLoading || initializedSiteToolProjectRef.current === id) return;
    initializedSiteToolProjectRef.current = id;
    selectZone(null);
    setActiveSitePlannerTool(null);
  }, [id, selectZone, setActiveSitePlannerTool, siteZones, siteZonesLoading]);

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
    setShowVideoRender(false);
    setMeasureActive(false);
    setShowHistory((open) => !open);
  }, []);

  // Master Plan tool: open Site Intelligence on the site boundary (or start drawing one).
  // Must clear every state that hides ZonePropertiesPanel (history, measure, step 2),
  // or the click is invisible and the button reads as dead.
  const handleMasterPlan = useCallback(() => {
    setMeasureActive(false);
    setShowHistory(false);
    setWorkflowStep(1);
    const boundary = getActiveSiteBoundary(siteZones);
    if (boundary) {
      setActiveSitePlannerTool(null);
      selectZone(boundary.id);
    } else {
      selectZone(null);
      setActiveSitePlannerTool('site_boundary');
      toast('Draw your site boundary first — the Master Plan tool analyzes everything inside it.', { icon: '🧠' });
    }
  }, [siteZones, selectZone, setActiveSitePlannerTool, setWorkflowStep]);

  const handleSiteBoundary = useCallback(() => {
    setMeasureActive(false);
    setShowHistory(false);
    setWorkflowStep(1);
    const boundary = getActiveSiteBoundary(siteZones);
    if (boundary) {
      setActiveSitePlannerTool(null);
      selectZone(boundary.id);
      return;
    }
    selectZone(null);
    setActiveSitePlannerTool('site_boundary');
  }, [siteZones, selectZone, setActiveSitePlannerTool, setWorkflowStep]);

  const masterPlanActive =
    workflowStep === 1 && !showHistory && selectedZone?.zone_type === 'site_boundary';

  const handleOpenGenerate3D = useCallback(async () => {
    if (!cityPromptWorkflow.canGenerate3D) {
      toast(cityPromptWorkflow.generationReason, { icon: '🏗️' });
      return;
    }
    if (visiblePlanLayers.length > 1) {
      toast('Choose one Master Planner scenario before generating 3D. “All” is for comparing alternatives, not building them on top of each other.', { icon: '🧭' });
      return;
    }
    setShowHistory(false);
    setMeasureActive(false);
    setShowGlobeRender(false);
    setShowVideoRender(false);
    selectZone(null);
    setIsPreparingGenerate3D(true);
    try {
      if (visibleZones.some((zone) => !isPersistedZoneId(zone.id))) {
        throw new Error('A plan zone is still saving. Wait a moment and run Generate to 3D again.');
      }
      const authoritativeProjectZones = id ? await siteZonesApi.list(id) : visibleZones;
      if (id) {
        // The server snapshot owns generation. Replacing the query cache here
        // also removes persisted-id ghost zones left by a backend restart or a
        // concurrent delete instead of misreporting them as "still saving".
        queryClient.setQueryData(['site-zones', id], authoritativeProjectZones);
      }
      const frozenVisibleZones = authoritativeProjectZones.filter((zone) => {
        const source = zone.properties?._imported_from;
        return !(typeof source === 'string' && hiddenLayers.has(source));
      });
      if (frozenVisibleZones.length === 0) {
        throw new Error('No saved building, park, or street is available to build. The plan was refreshed; draw the zone again.');
      }
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      setGenerate3DZones(frozenVisibleZones);
      setShowLegoBuilder(true);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Could not prepare Generate to 3D.');
    } finally {
      setIsPreparingGenerate3D(false);
    }
  }, [cityPromptWorkflow, hiddenLayers, id, queryClient, selectZone, visiblePlanLayers, visibleZones]);

  const handleCloseGenerate3D = useCallback(() => {
    setShowLegoBuilder(false);
    setGenerate3DZones(null);
  }, []);

  const handleOpenGlobeRender = useCallback(() => {
    if (!cityPromptWorkflow.canRender) {
      toast(cityPromptWorkflow.renderReason, { icon: '🧱' });
      return;
    }
    setShowHistory(false);
    setMeasureActive(false);
    setShowVideoRender(false);
    setGlobeRenderPosition(null);
    setShowGlobeRender(true);
    setShowProjectRenders(false);
  }, [cityPromptWorkflow]);

  const handleOpenVideoRender = useCallback(() => {
    if (!cityPromptWorkflow.canRender) {
      toast(cityPromptWorkflow.renderReason, { icon: '🧱' });
      return;
    }
    setShowHistory(false);
    setMeasureActive(false);
    setShowGlobeRender(false);
    selectZone(null);
    setShowVideoRender(true);
  }, [cityPromptWorkflow, selectZone]);

  const handleWorkflowStepClick = useCallback((step: CityPromptWorkflowStep) => {
    if (step === 1) {
      setWorkflowStep(1);
      setShowGlobeRender(false);
      setShowVideoRender(false);
      const boundary = cityPromptWorkflow.activeBoundary;
      if (boundary) {
        setActiveSitePlannerTool(null);
        selectZone(boundary.id);
      } else {
        selectZone(null);
        setActiveSitePlannerTool('site_boundary');
      }
      return;
    }
    if (step === 2) {
      handleMasterPlan();
      return;
    }
    if (step === 3) {
      handleOpenGenerate3D();
      return;
    }
    if (settings.mapMode === 'globe') handleOpenGlobeRender();
    else setWorkflowStep(2);
  }, [
    cityPromptWorkflow.activeBoundary,
    handleMasterPlan,
    handleOpenGenerate3D,
    handleOpenGlobeRender,
    selectZone,
    setActiveSitePlannerTool,
    setWorkflowStep,
    settings.mapMode,
  ]);

  // Presentation navigation is transient UI state; the saved design and camera stay authoritative.
  const activeStudentStep = studentStep ?? (cityPromptWorkflow.activeBoundary ? 'design' : 'site');
  const changeStudentStep = (step: StudentStep) => {
    cancelPlacement();
    selectZone(null);
    setActiveSitePlannerTool(null);
    useViewerStore.getState().setStreetViewActive(false);
    setMeasureActive(false);
    setShowHistory(false);
    setShowGlobeRender(false);
    setShowVideoRender(false);
    setShowReferenceLayers(false);
    setStudentStep(step);
  };

  const prepareForAIRenderCapture = useCallback(async () => {
    const tilesSettled = await globeRefs?.waitForTilesSettled?.();
    if (tilesSettled === false) {
      throw new Error('Google 3D detail is still loading. Keep this view still for a few seconds, then try the render again. No credits were used.');
    }
    if (useViewerStore.getState().selectedZoneId) {
      selectZone(null);
    }
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  }, [globeRefs, selectZone]);

  const prepareForVideoCapture = useCallback(async () => {
    if (useViewerStore.getState().selectedZoneId) selectZone(null);
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
  const [activeAIStyle, setActiveAIStyle] = useState('photorealistic');
  const autoSavedRenderKeysRef = useRef<Set<string>>(new Set());

  const rememberSavedRender = useCallback((render: SavedRender) => {
    setSavedRenders((current) => [render, ...current.filter((item) => item.id !== render.id)]);
    // The render panel already shows the result. The gallery badge updates
    // without opening another floating panel over the tablet controls.
  }, []);

  const rememberSavedVideo = useCallback((attempt: VideoAttempt) => {
    if (!attempt.video_url || attempt.status !== 'complete') return;
    setSavedVideos((current) => [attempt, ...current.filter((item) => item.id !== attempt.id)]);
    setShowProjectRenders(true);
  }, []);

  const handleEditRender = useCallback((render: SavedRender) => {
    setRenderEditTarget(render);
    setRenderLightbox(null);
  }, []);

  const refreshSavedRenders = useCallback(() => {
    if (!id) return;
    rendersApi.list(id).then(setSavedRenders).catch(() => {});
  }, [id]);

  const autoSaveAIRenders = useCallback((renders: AIRenderResult[], style: string) => {
    if (!id || renders.length === 0) return;

    const unsaved = renders.map((render, index) => ({ render, index, key: getRenderImageKey(render) })).filter(({ key }) => {
      if (autoSavedRenderKeysRef.current.has(key)) return false;
      autoSavedRenderKeysRef.current.add(key);
      return true;
    });

    if (unsaved.length === 0) return;

    Promise.allSettled(
      unsaved.map(({ render, index }) => saveRenderedImage(
        id,
        render,
        renders.length > 1 ? `${style} preview ${index + 1}` : style,
      )),
    ).then((results) => {
      results.forEach((result, index) => {
        if (result.status === 'rejected') {
          autoSavedRenderKeysRef.current.delete(unsaved[index].key);
        }
      });
      const saved = results
        .filter((result): result is PromiseFulfilledResult<SavedRender> => result.status === 'fulfilled')
        .map((result) => result.value);

      if (saved.length === 0) return;
      setSavedRenders((current) => [
        ...saved,
        ...current.filter((item) => !saved.some((render) => render.id === item.id)),
      ]);
      setShowProjectRenders(true);
    }).catch(() => undefined);
  }, [id]);

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

  /** When AIRenderPanel produces previews, persist them and return to the project workspace. */
  const handlePreviewsReady = useCallback((previews: AIRenderResult[]) => {
    setRenderPreviews(previews);
    setRenderModalSelectedIdx(null);
    setFullRenderResult(null);
    setShowRenderModal(false);
    autoSaveAIRenders(previews, activeAIStyle);
    setWorkflowStep(1);
  }, [activeAIStyle, autoSaveAIRenders, setWorkflowStep]);

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

  const renderViewerActive = showRenderModal || showGlobeRender || showVideoRender || !!renderLightbox || !!renderEditTarget || !!lightboxImageUrl || aiPanelLightboxOpen;

  const stepRenderLightbox = useCallback((direction: -1 | 1) => {
    setRenderLightbox((current) => {
      if (!current || savedRenders.length < 2) return current;
      const sequence = current.variant === 'provider_original' ? savedRenders
        : savedRenders.filter((render) => render.variant !== 'provider_original');
      const currentIndex = sequence.findIndex((render) => render.id === current.id);
      const startIndex = currentIndex >= 0 ? currentIndex : 0;
      const nextIndex = (startIndex + direction + sequence.length) % sequence.length;
      return sequence[nextIndex] ?? current;
    });
  }, [savedRenders]);


  useEffect(() => {
    if (!renderLightbox) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't hijack keys while typing in a field (e.g. the Edit Render box).
      if (isTextEntryTarget(e.target)) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        setRenderLightbox(null);
        return;
        }

        if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          stepRenderLightbox(-1);
          return;
        }

        if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          stepRenderLightbox(1);
          return;
        }

        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
        }
      };

      window.addEventListener('keydown', handleKeyDown, true);
      return () => window.removeEventListener('keydown', handleKeyDown, true);
  }, [renderLightbox, stepRenderLightbox]);

  const { data: project, isLoading, error: projectError, refetch: reloadProject } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      const hasGenerating = data.buildings?.some(
        (b: { generation_status?: string }) => b.generation_status === 'generating'
      );
      return hasGenerating ? 3000 : 10 * 60 * 1000;
    },
  });

  const visibleBuildings = useMemo(
    () => filterBuildingsForVisibleCommunity3DScope(
      project?.buildings ?? [],
      siteZones,
      visibleZones,
    ),
    [project?.buildings, siteZones, visibleZones],
  );
  const automatic3D = useAutomatic3D(project && project.permission !== 'viewer' && settings.mapMode === 'globe' ? id : undefined, siteZones, isSaving);
  videoCaptureSceneRef.current = { projectId: id, zones: visibleZones, buildings: visibleBuildings };

  const deleteModeledBuilding = useMutation({
    mutationFn: async (buildingId: string) => {
      const owner = catalogueZoneForBuilding(buildingId, project?.buildings ?? [], siteZones);
      if (owner) {
        await deleteZone.mutateAsync(owner.id);
        return 'catalogue';
      }
      try { await buildingsApi.delete(buildingId); } catch (error) {
        if ((error as { response?: { status?: number } }).response?.status !== 404) throw error;
        const latest = await projectsApi.get(id!);
        if (latest.buildings?.some(building => building.id === buildingId)) throw error;
        queryClient.setQueryData(['project', id], latest);
      }
      return 'model';
    },
    onSuccess: async (_result, buildingId) => {
      setModeledBuildingIds((previous) => {
        const next = new Set(previous);
        next.delete(buildingId);
        return next;
      });
      await queryClient.invalidateQueries({ queryKey: ['project', id] });
      await queryClient.invalidateQueries({ queryKey: ['site-zones', id] });
      if (_result === 'model') toast.success('3D model deleted');
    },
    onError: (error: Error) => toast.error(`Failed to delete 3D model: ${error.message}`),
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
  if (!project) return <div role="alert" className="mx-auto max-w-lg space-y-4 rounded-xl bg-white p-6 text-slate-800">
    <h1 className="text-xl font-semibold">{projectError ? 'Your project could not load' : 'Project not found'}</h1>
    <p>{projectError ? 'Check your connection and try again. A loading problem does not mean your saved work has been deleted.' : 'The project may have been removed or your access may have changed.'}</p>
    <button onClick={() => { void reloadProject(); }} className="btn-primary min-h-11">Try again</button>
    <Link to="/projects" className="ml-4 underline">Your projects</Link>
  </div>;

  if (project.permission === 'viewer') return <ReadOnlyProject project={project} zones={siteZones} renders={savedRenders} videos={savedVideos} />;

  const globeRenderZones = withModeledBuildingRenderZones(
    visibleZones,
    visibleBuildings,
    modeledBuildingIds,
    project.id,
  );

  // --- Globe mode: full-screen Google 3D Tiles ---
  if (settings.mapMode === 'globe') {
    return (
      <div className="fixed inset-x-0 bottom-0 top-16 z-50 bg-black">
        <Suspense fallback={<MapLoadingFallback mode="3D" />}>
          <GlobeSitePlannerMap
            placementDraft={placementDraft}
            onPlacementDraftChange={setPlacementDraft}
            parkGroundPaused={isSaving || automatic3D.busy}
            onAutoParkTerrain={(zone, profile) => saveAutomaticParkGround(queryClient, project.id, zone, profile)}
            onFollowParkTerrain={async profiles => {
              // Save each measured park first. Only remove the whole-site plane
              // once every dependent surface has been confirmed by the API.
              for (const [zoneId, profile] of Object.entries(profiles)) {
                const park = siteZones.find(z => z.id === zoneId);
                if (!park) throw new Error('Park no longer exists');
                await updateZone.mutateAsync({ zoneId, data: { properties: { ...park.properties,
                  park_terrain: profile, proposed_terrace: null, community_3d_mask_existing_tiles: true,
                } }, previousData: { properties: park.properties } });
              }
              const boundary = getActiveSiteBoundary(siteZones);
              if (!boundary) throw new Error('Site no longer exists');
              await updateZone.mutateAsync({ zoneId: boundary.id, data: { properties: { ...boundary.properties,
                terrain_strategy: 'landscape', community_3d_mask_existing_tiles: false,
              } }, previousData: { properties: boundary.properties } });
            }}
            onPrepareGround={async (zoneId, clear, height, edges) => {
              const boundary = siteZones.find(zone => zone.id === zoneId);
              if (!boundary) throw new Error('Site boundary no longer exists');
              await updateZone.mutateAsync({ zoneId, data: { properties: { ...boundary.properties,
                community_3d_mask_existing_tiles: clear,
                terrain_strategy: null,
                ...(height !== undefined ? { terrain_elevation_m: height } : {}),
                ...(edges !== undefined ? { terrain_edge_profile: edges } : {}),
              } }, previousData: { properties: boundary.properties } });
            }}
            onPlaceAsset={placeObject}
            onCancelPlacement={cancelPlacement}
            latitude={project.location?.latitude}
            longitude={project.location?.longitude}
            siteZones={visibleZones}
            allSiteZones={siteZones}
            referenceLayers={references.visibleLayers}
            transportContext={transportContext}
            buildings={visibleBuildings}
            onZoneCreated={(coordinates, type, properties) => {
              if (isFixedSectionStreet({zone_type:type, properties})) {
                const problem = streetRouteProblem(coordinates, streetSectionWidth({zone_type:type, properties})) ?? placementProblem(coordinates, siteZones, getActiveSiteBoundary(siteZones));
                if (problem) { toast.error(problem, {position:'top-center'}); return false; }
              }
              handleZoneCreated(coordinates, type, properties);
            }}
            onZoneUpdated={reshapeObject}
            onZoneSelected={(zoneId) => { if (zoneId) selectZone(zoneId); else selectZone(null); }}
            onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
            onBuildingDeleted={(buildingId) => deleteModeledBuilding.mutate(buildingId)}
            onGlobeReady={setGlobeRefs}
            onModeledBuildingsChange={setModeledBuildingIds}
            measureModeActive={measureActive}
            interactionPaused={renderViewerActive || showPlanningReport || showShare || showTour || showReferenceLayers || showCatalogue}
            onMeasureModeChange={handleMeasureModeChange}
          />
        </Suspense>

        {/* Toolbar - hidden on phones during focused vertex placement. */}
        <div
          className={`pointer-events-none absolute inset-x-3 top-44 z-30 min-h-0 overflow-y-auto overscroll-contain sm:inset-x-auto sm:left-4 sm:top-28 sm:bottom-16 sm:w-64 sm:max-h-none sm:overflow-y-auto sm:pr-2 ${activeSitePlannerTool || placementDraft || (selectedZone && (assetForZone(selectedZone) || isFixedSectionStreet(selectedZone))) ? 'hidden sm:block' : 'bottom-3 max-h-[60dvh]'}`}
        >
          <div className="pointer-events-auto h-full">
            <StudentWorkflowNav step={activeStudentStep} onChange={changeStudentStep} />
            {activeStudentStep !== 'design' && !showGlobeRender && !showVideoRender && <StudentStepPanel
              step={activeStudentStep} hasSite={Boolean(cityPromptWorkflow.activeBoundary && isPersistedZoneId(cityPromptWorkflow.activeBoundary.id))}
              drawingSite={activeSitePlannerTool === 'site_boundary'} location={project.location?.address}
              canRender={cityPromptWorkflow.canRender} renderReason={cityPromptWorkflow.renderReason}
              onSite={() => { setStudentStep('site'); handleSiteBoundary(); }} onDesign={() => changeStudentStep('design')}
              onImage={handleOpenGlobeRender} onVideo={handleOpenVideoRender} />}
            <div hidden={activeStudentStep !== 'design'}>
            <SitePlannerToolbar
              streetPlacement={CALGARY_LOCAL_PLACEMENT}
              streetInPlacement
              placementSlot={<PlacementPalette selected={placementDraft?.assetId ?? null} onPick={pickObject} onCancel={cancelPlacement}
                status={automatic3D.status} message={automatic3D.message} onRetry={automatic3D.retry}
                onBrowseChange={setShowCatalogue}
                onPickCanonical={selection => {
                  if (selection.choice.domain === 'building') {
                    pickObject(canonicalBuildingAsset(selection).id);
                    return;
                  }
                  cancelPlacement(); selectZone(null); setMeasureActive(false);
                  useViewerStore.getState().setStreetViewActive(false);
                  const drawing = canonicalDrawing(selection);
                  setActiveSitePlannerTool(drawing.type, drawing.properties);
                }}
                activeStreetVariant={activeSitePlannerTool === 'road' ? String(activeToolProperties?.road_selected_variant_id ?? '') : undefined}
                onPickStreet={asset => {
                  cancelPlacement(); selectZone(null); setMeasureActive(false);
                  useViewerStore.getState().setStreetViewActive(false);
                  setActiveSitePlannerTool('road', asset.properties);
                }} />}
              onLeavePlacement={cancelPlacement}
              layout="sidebar"
              isGlobeMode
              onShowGuide={() => setShowTour(true)}
              onToggleHistory={handleToggleHistory}
              historyOpen={showHistory}
              measureActive={measureActive}
              onMeasureModeChange={handleMeasureModeChange}
              onMasterPlan={handleMasterPlan}
              masterPlanActive={masterPlanActive}
              onSiteBoundary={handleSiteBoundary}
              bottomSlot={
                !showGlobeRender && !showVideoRender ? (
                  <div className="flex flex-col gap-1">
                    <StudioSaveStatus saving={isSaving} draftCount={pendingDrafts.length} draftsPersistOnDevice={draftsPersistOnDevice} loadError={Boolean(siteZonesError)} onRetry={() => pendingDrafts.forEach(retryDraft)} onReload={() => { void reloadSavedVersion(); }}
                      discardableCount={discardableDrafts.length} onDiscardRejected={() => discardableDrafts.forEach(discardDraft)} saveError={saveError} />
                    <details><summary className="min-h-11 cursor-pointer py-3 text-xs text-slate-700">Project steps &amp; custom 3D</summary>
                    <WorkflowStepper
                      state={cityPromptWorkflow}
                      activeStep={showLegoBuilder ? 3 : cityPromptWorkflow.currentStep}
                      onStepClick={handleWorkflowStepClick}
                      compact
                    />
                    <button
                      data-tour="generate-3d-btn"
                      onClick={handleOpenGenerate3D}
                      disabled={!cityPromptWorkflow.canGenerate3D || isPreparingGenerate3D}
                      title={cityPromptWorkflow.generationReason}
                      className="flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-gradient-to-r from-[#28c7e8] to-[#c9ff3d] px-3 py-2.5 text-sm font-black uppercase text-[#151515] shadow-[4px_4px_0_0_#151515] transition hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_0_#151515] disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      <Blocks size={16} />
                      {isPreparingGenerate3D ? 'Preparing…' : 'Generate to 3D'}
                    </button></details>
                    <button type="button" data-tour="ai-render-btn" onClick={() => changeStudentStep('present')}
                      className="flex min-h-11 w-full items-center justify-center gap-2 rounded-lg border-2 border-slate-950 bg-[#c9ff3d] px-3 py-2 text-sm font-bold text-slate-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-700">
                      <Camera size={16} aria-hidden /> Render this view
                    </button>
                  </div>
                ) : null
              }
            />
            </div>
          </div>
        </div>

        <div className="absolute right-3 top-16 z-40 max-w-[calc(100vw-1.5rem)] sm:right-4 sm:top-2">
          <StudioControls layersOpen={showReferenceLayers} onLayers={() => { selectZone(null); setShowReferenceLayers((open) => !open); }}
            onReport={() => { setActiveSitePlannerTool(null); setShowPlanningReport(true); }} onTeam={() => setShowShare(true)} onHelp={() => setShowTour(true)} />
        </div>
        {showReferenceLayers && !showPlanningReport && <aside aria-label="Map layers" className="absolute bottom-20 right-3 top-32 z-40 flex max-w-[calc(100vw-1.5rem)] flex-col gap-3 overflow-y-auto rounded-xl bg-white/95 p-3 shadow-xl sm:right-4 sm:top-20">
          <div className="sticky -top-3 z-10 flex items-center justify-between bg-white py-1"><h2 className="font-semibold text-slate-900">Map layers</h2><button onClick={() => setShowReferenceLayers(false)} aria-label="Close layers" className="flex h-11 w-11 items-center justify-center"><X size={18} /></button></div>
          <ShapefileImportButton projectId={project.id} />
          <CalgaryContextButton projectId={project.id} zones={siteZones} layers={references.layers} />
          <ReferenceLayersPanel layers={references.layers} hiddenIds={references.hiddenIds} onToggle={references.toggleLayer}
            onDelete={references.canEdit ? references.removeLayer : undefined} deletingId={references.deletingId}
            isLoading={references.isLoading} error={references.error} onRetry={() => { void references.refetch(); }} />
          <LayersPanel siteZones={siteZones} hiddenLayers={hiddenLayers} onToggleLayer={toggleLayer} onDeleteLayer={deleteLayer} deletingLayer={deletingLayer} />
          <SiteElevation lat={project.location?.latitude} lon={project.location?.longitude} />
        </aside>}
        {showPlanningReport && <StudioDialog title="Planning report" onClose={closePlanningReport}>
          <TerraceSummary zones={siteZones}/>
          <StudentPlanningReport projectId={project.id} zoneIds={visibleZones.filter((zone) => isPersistedZoneId(zone.id)).map((zone) => zone.id)}
            planChangeToken={siteZones.map((zone) => `${zone.id}:${zone.updated_at}`).join('|')} canEdit
            onSelectZone={(zoneId) => { closePlanningReport(); selectZone(zoneId); }} />
        </StudioDialog>}
        {showShare && <ShareModal projectId={project.id} projectName={project.name} onClose={() => setShowShare(false)} />}
        {showTour && <OnboardingTour placementMode forceShow onComplete={() => setShowTour(false)} />}

        {/* Zone properties panel */}
        {selectedZone && assetForZone(selectedZone) && advancedZoneId !== selectedZone.id && !placementDraft && !showHistory && !measureActive && (
          <ReshapePanel key={`${selectedZone.id}:${JSON.stringify(selectedZone.coordinates)}`} zone={selectedZone} disabled={isSaving}
            onUpdateDesign={properties => updateZone.mutate({ zoneId: selectedZone.id, data: { properties }, previousData: { properties: selectedZone.properties } })}
            onTerrace={['building','residential','green_space'].includes(selectedZone.zone_type)?()=>setTerraceZoneId(selectedZone.id):undefined}
            onConnections={()=>setConnectionZoneId(selectedZone.id)}
            onReshape={coordinates => reshapeObject(selectedZone.id, coordinates)} onClose={() => selectZone(null)}
            onDelete={() => deleteZone.mutate(selectedZone.id)} onDuplicate={pickObject} onMore={() => setAdvancedZoneId(selectedZone.id)} />
        )}
        {selectedZone && isFixedSectionStreet(selectedZone) && advancedZoneId !== selectedZone.id && !placementDraft && !showHistory && !measureActive && (
          <StreetRoutePanel zone={selectedZone} disabled={isSaving} onReshape={coords=>reshapeObject(selectedZone.id, coords)}
            connectionLeavesSite={publicRoadConnectionFits(selectedZone, selectedZone.coordinates, getActiveSiteBoundary(siteZones))}
            onPublicConnection={enabled => updateZone.mutate({zoneId: selectedZone.id, data: {
              properties: {...selectedZone.properties, connect_to_public_road: enabled},
            }, previousData: { properties: selectedZone.properties }})}
            onConnections={()=>setConnectionZoneId(selectedZone.id)}
            onClose={()=>selectZone(null)} onDelete={()=>deleteZone.mutate(selectedZone.id)} onMore={()=>setAdvancedZoneId(selectedZone.id)} />
        )}
        {selectedZone && ((!assetForZone(selectedZone) && !isFixedSectionStreet(selectedZone)) || advancedZoneId === selectedZone.id) && !showHistory && !measureActive && (
          <ZonePropertiesPanel
            key={selectedZone.id}
            belowGlobeControls
            zone={selectedZone}
            savedVersionReload={savedVersionReload}
            onConnections={['building','residential','green_space','road'].includes(selectedZone.zone_type) ? ()=>setConnectionZoneId(selectedZone.id) : undefined}
            onUpdate={(zoneId, data) => {
              const previousZone = siteZones.find((z) => z.id === zoneId);
              updateZone.mutate({
                zoneId,
                data,
                previousData: previousZone
                  ? { name: previousZone.name, color: previousZone.color, properties: previousZone.properties }
                  : undefined,
              });
              if (siteZones) rebufferRoadOnUpdate(zoneId, data, siteZones, handleZoneUpdated);
            }}
            onDelete={(zoneId) => deleteZone.mutate(zoneId)}
            onClose={() => selectZone(null)}
            onAIGenerate={(buildingId) => setAiGenerateBuildingId(buildingId)}
            onOpenBlockEditor={(draftZone) => setLegoZone(draftZone)}
            buildings={project.buildings}
            allZones={siteZones}
          />
        )}

        {terraceZone && <TerraceEditor key={terraceZone.id} zone={terraceZone} zones={siteZones} disabled={isSaving} onClose={()=>setTerraceZoneId(null)} onSave={async properties=>{
          await updateZone.mutateAsync({zoneId:terraceZone.id,data:{properties},previousData:{properties:terraceZone.properties}});
        }}/>}
        {connectionZone && <ConnectionEditor key={connectionZone.id} zone={connectionZone} zones={siteZones} transportContext={transportContext} visibleIds={visibleZones.map(zone=>zone.id)} disabled={isSaving}
          onClose={()=>setConnectionZoneId(null)} onSave={async properties=>{
            await updateZone.mutateAsync({zoneId:connectionZone.id,data:{properties},previousData:{properties:connectionZone.properties}});
          }} />}
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
                siteZones={globeRenderZones}
                communitySourceZones={visibleZones}
                buildings={visibleBuildings}
                terrainHeight={globeRefs?.terrainHeight ?? 1045}
                projectId={project?.id}
                selectedZoneId={selectedZoneId}
                modeledBuildingIds={modeledBuildingIds}
                setBuildingModelsVisible={globeRefs?.setBuildingModelsVisible}
                captureDirect3D={globeRefs?.captureDirect3D}
                onBeforeRender={prepareForAIRenderCapture}
                isDragging={isDraggingGlobeRender}
                onLightboxOpenChange={setAiPanelLightboxOpen}
                onRenderSaved={rememberSavedRender}
                dragHandleProps={{
                  onPointerDown: handleGlobeRenderDragStart,
                }}
                onClose={() => setShowGlobeRender(false)}
              />
            </div>
          </div>
        )}

        {showVideoRender && id && (
          <VideoGeneratePanel
            projectId={id}
            canvas={globeRefs?.canvas ?? null}
            siteZones={visibleZones}
            buildings={visibleBuildings}
            waitForTilesSettled={globeRefs?.waitForTilesSettled}
            onBeforeCapture={prepareForVideoCapture}
            captureAerialFrame={captureVideoAerialFrame}
            captureRouteControls={captureVideoRouteControls}
            onVideoSaved={rememberSavedVideo}
            onClose={() => setShowVideoRender(false)}
          />
        )}

        {/* Back button */}
        <div className="absolute left-4 top-4 z-30 flex max-w-[calc(100vw-2rem)] items-center gap-3 sm:top-2 sm:max-w-[calc(100vw-26rem)]">
          <Link to="/projects" aria-label="Back to projects" className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-gray-900/90 backdrop-blur-sm hover:bg-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-white">
            <ArrowLeft size={18} className="text-white" />
          </Link>
          <span className="min-w-0 max-w-[calc(100vw-5.5rem)] truncate rounded-lg bg-slate-950/85 px-3 py-2 text-sm font-medium text-white sm:max-w-sm">
            {project.name}
          </span>
        </div>

        {/* Street View Panel — with globe 3D tiles capture */}

        <ProjectRendersTray
          renders={savedRenders}
          videos={savedVideos}
          open={showProjectRenders}
          onToggle={() => setShowProjectRenders((open) => !open)}
          onClose={() => setShowProjectRenders(false)}
          onSelect={setRenderLightbox}
          onSelectVideo={setVideoLightbox}
        />

        <StreetViewPanel
          siteZones={visibleZones}
          projectId={project?.id}
          globeCapture={handleGlobeStreetCapture}
          buildings={visibleBuildings}
          onRenderSaved={rememberSavedRender}
        />

        {renderLightbox && (
          <div
            className="fixed inset-0 z-[250] flex items-center justify-center bg-black/80 backdrop-blur-sm"
            onClick={() => setRenderLightbox(null)}
          >
            <div className="relative max-h-[90vh] max-w-[90vw]" onClick={(event) => event.stopPropagation()}>
              <img
                src={resolveApiFileUrl(renderLightbox.image_url)}
                alt={renderLightbox.prompt || 'Saved render'}
                className="max-h-[85vh] max-w-full rounded-xl object-contain shadow-2xl"
              />
              {savedRenders.length > 1 && (
                <>
                  <button
                    type="button"
                    onClick={() => stepRenderLightbox(-1)}
                    className="absolute left-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-black/60 text-white/85 shadow-lg ring-1 ring-white/20 transition hover:bg-black/80 hover:text-white"
                    aria-label="Previous render"
                    title="Previous render (Left or A)"
                  >
                    <ArrowLeft size={20} />
                  </button>
                  <button
                    type="button"
                    onClick={() => stepRenderLightbox(1)}
                    className="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-black/60 text-white/85 shadow-lg ring-1 ring-white/20 transition hover:bg-black/80 hover:text-white"
                    aria-label="Next render"
                    title="Next render (Right or D)"
                  >
                    <ArrowLeft size={20} className="rotate-180" />
                  </button>
                </>
              )}
              <div className="absolute bottom-0 left-0 right-0 rounded-b-xl bg-gradient-to-t from-black/80 to-transparent px-5 py-4">
                {renderLightbox.prompt && (
                  <p className="text-sm text-white/90 line-clamp-2">{renderLightbox.prompt}</p>
                )}
                <p className="mt-1 text-xs text-white/50">
                  {new Date(renderLightbox.created_at).toLocaleDateString()}
                  {renderLightbox.style && ` · ${renderLightbox.style}`}
                </p>
                <RenderSourceNote render={renderLightbox} />
              </div>
              <div className="absolute top-3 right-3 flex gap-2">
                <button
                  type="button"
                  onClick={() => handleEditRender(renderLightbox)}
                  className="flex items-center gap-2 rounded-full bg-amber-400 px-3 py-2 text-xs font-bold text-black shadow-lg shadow-black/30 ring-1 ring-white/20 transition hover:bg-amber-300"
                  title="Edit masked area"
                  aria-label="Edit render"
                >
                  <Wand2 size={16} />
                  Edit Render
                </button>
                <a
                  href={resolveApiFileUrl(renderLightbox.image_url)}
                  download={`render-${renderLightbox.id}.png`}
                  className="rounded-full bg-black/60 p-2 text-white/80 transition hover:bg-black/80 hover:text-white"
                  title="Download"
                >
                  <FileDown size={18} />
                </a>
                <button
                  onClick={() => setRenderLightbox(null)}
                  className="rounded-full bg-black/60 p-2 text-white/80 transition hover:bg-black/80 hover:text-white"
                  aria-label="Close render"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
          </div>
        )}

        {videoLightbox?.video_url && (
          <div
            className="fixed inset-0 z-[250] flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
            onClick={() => setVideoLightbox(null)}
          >
            <div className="relative w-full max-w-6xl overflow-hidden rounded-xl bg-black shadow-2xl ring-1 ring-white/15" onClick={(event) => event.stopPropagation()}>
              <video
                src={resolveApiFileUrl(videoLightbox.video_url)}
                controls
                autoPlay
                playsInline
                className="aspect-video w-full bg-black object-contain"
              />
              <div className="flex items-center gap-3 bg-[#151515] px-4 py-3 text-white">
                <Video size={18} className="text-[#c9ff3d]" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-bold capitalize">{videoRenderLabel(videoLightbox)}</p>
                  <p className="text-xs text-white/50">8 sec · {videoProviderOrigin(videoLightbox)} · saved to project</p>
                </div>
                <a
                  href={videoDownloadUrl(videoLightbox)}
                  download
                  className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-2 text-xs font-black uppercase text-[#151515] hover:bg-[#f7f2e8]"
                >
                  <FileDown size={16} /> Download MP4
                </a>
                <button onClick={() => setVideoLightbox(null)} className="rounded-full bg-white/10 p-2 hover:bg-white/20" aria-label="Close video">
                  <X size={18} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Double-click a variant to open large preview */}
        <ImageLightbox />
        {id && renderEditTarget && (
          <RenderEditModal
            projectId={id}
            render={renderEditTarget}
            imageUrl={resolveApiFileUrl(renderEditTarget.image_url)}
            onSaved={rememberSavedRender}
            onClose={() => setRenderEditTarget(null)}
          />
        )}

        {/* LEGO assembly composer — modular building preview + saved recipes */}
        {legoZone && (
          <LegoAssemblyPreview
            zone={legoZone}
            buildingId={legoZone.building_id ?? legoZone.building_ids?.[0] ?? null}
            onClose={() => setLegoZone(null)}
          />
        )}

        {/* LEGO builder — the whole plan assembled from archetype modules */}
        {showLegoBuilder && (
          <LegoBuilderPanel
            zones={generate3DZones ?? visibleZones}
            autoGenerate
            onClose={handleCloseGenerate3D}
          />
        )}
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
          state={cityPromptWorkflow}
          activeStep={workflowStep === 2 ? 4 : cityPromptWorkflow.currentStep}
          onStepClick={handleWorkflowStepClick}
        />

        <div className="relative h-[56vh] min-h-[430px] sm:h-[62vh] lg:h-[68vh]">
          <Suspense fallback={<MapLoadingFallback mode="2D" />}>
            <SitePlannerMap
              latitude={project.location?.latitude}
              longitude={project.location?.longitude}
              siteZones={siteZones}
              onZoneCreated={handleZoneCreated}
              onZoneUpdated={handleZoneUpdated}
              onZoneSelected={handleZoneSelected}
              onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
              interactionPaused={renderViewerActive}
            />
          </Suspense>
          {/* GIS color legend */}
          <ZoneLegend siteZones={siteZones} />

          {/* Street View Panel */}
          <StreetViewPanel siteZones={siteZones} projectId={project?.id} onRenderSaved={rememberSavedRender} />

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
              savedVersionReload={savedVersionReload}
              onUpdate={(zoneId, data) => {
                const previousZone = siteZones.find((z) => z.id === zoneId);
                updateZone.mutate({
                  zoneId,
                  data,
                  previousData: previousZone
                    ? { name: previousZone.name, color: previousZone.color, properties: previousZone.properties }
                    : undefined,
                });
                // Re-buffer road polygon when width changes
                if (siteZones) {
                  rebufferRoadOnUpdate(zoneId, data, siteZones, handleZoneUpdated);
                }
              }}
              onDelete={(zoneId) => deleteZone.mutate(zoneId)}
              onClose={() => selectZone(null)}
              onAIGenerate={(buildingId) => setAiGenerateBuildingId(buildingId)}
              onOpenBlockEditor={(draftZone) => setLegoZone(draftZone)}
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
              onLightboxOpenChange={setAiPanelLightboxOpen}
              onStyleChange={setActiveAIStyle}
              onRenderSaved={rememberSavedRender}
            />
          )}

          <ProjectRendersTray
            renders={savedRenders}
            videos={savedVideos}
            open={showProjectRenders}
            onToggle={() => setShowProjectRenders((open) => !open)}
            onClose={() => setShowProjectRenders(false)}
            onSelect={setRenderLightbox}
            onSelectVideo={setVideoLightbox}
          />

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
        <div className="flex min-h-0 items-center justify-between gap-3 px-4 py-2 bg-gray-900 border-t border-gray-800">
          <div className="flex-1 min-w-0">
            <SitePlannerToolbar
              onShowGuide={() => setShowTour(true)}
              onToggleHistory={handleToggleHistory}
              historyOpen={showHistory}
              onMasterPlan={handleMasterPlan}
              masterPlanActive={masterPlanActive}
              onSiteBoundary={handleSiteBoundary}
            />
          </div>

          {/* Plan editing actions: compile the scene before image rendering. */}
          {workflowStep === 1 && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleOpenGenerate3D}
                disabled={!cityPromptWorkflow.canGenerate3D || isPreparingGenerate3D}
                className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                title={cityPromptWorkflow.generationReason}
              >
                <Blocks size={16} />
                {isPreparingGenerate3D ? 'Preparing…' : 'Generate to 3D'}
              </button>
              <button
                data-tour="ai-render-btn"
                onClick={() => setWorkflowStep(2)}
                disabled={!cityPromptWorkflow.canRender}
                className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                title={cityPromptWorkflow.renderReason}
              >
                <Sparkles size={16} />
                AI Render
              </button>
            </div>
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
                No saved renders yet. Aerial and street-view renders save here automatically as they complete.
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
          {/* LEGO assembly composer — modular building preview + saved recipes */}
          {legoZone && (
            <LegoAssemblyPreview
              zone={legoZone}
              buildingId={legoZone.building_id ?? legoZone.building_ids?.[0] ?? null}
              onClose={() => setLegoZone(null)}
            />
          )}
          {/* LEGO builder — the whole plan assembled from archetype modules */}
          {showLegoBuilder && (
            <LegoBuilderPanel
              zones={generate3DZones ?? visibleZones}
              autoGenerate
              onClose={handleCloseGenerate3D}
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
            {savedRenders.length > 1 && (
              <>
                <button
                  type="button"
                  onClick={() => stepRenderLightbox(-1)}
                  className="absolute left-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-black/60 text-white/85 shadow-lg ring-1 ring-white/20 transition hover:bg-black/80 hover:text-white"
                  aria-label="Previous render"
                  title="Previous render (Left or A)"
                >
                  <ArrowLeft size={20} />
                </button>
                <button
                  type="button"
                  onClick={() => stepRenderLightbox(1)}
                  className="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-black/60 text-white/85 shadow-lg ring-1 ring-white/20 transition hover:bg-black/80 hover:text-white"
                  aria-label="Next render"
                  title="Next render (Right or D)"
                >
                  <ArrowLeft size={20} className="rotate-180" />
                </button>
              </>
            )}
            <div className="absolute bottom-0 left-0 right-0 rounded-b-xl bg-gradient-to-t from-black/80 to-transparent px-5 py-4">
              {renderLightbox.prompt && (
                <p className="text-sm text-white/90 line-clamp-2">{renderLightbox.prompt}</p>
              )}
              <p className="mt-1 text-xs text-white/50">
                {new Date(renderLightbox.created_at).toLocaleDateString()}
                {renderLightbox.style && ` · ${renderLightbox.style}`}
              </p>
              <RenderSourceNote render={renderLightbox} />
            </div>
            <div className="absolute top-3 right-3 flex gap-2">
              <button
                type="button"
                onClick={() => handleEditRender(renderLightbox)}
                className="flex items-center gap-2 rounded-full bg-amber-400 px-3 py-2 text-xs font-bold text-black shadow-lg shadow-black/30 ring-1 ring-white/20 transition hover:bg-amber-300"
                title="Edit masked area"
                aria-label="Edit render"
              >
                <Wand2 size={16} />
                Edit Render
              </button>
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
          style={activeAIStyle}
          onSaved={() => {
            refreshSavedRenders();
          }}
        />
      )}
      {id && renderEditTarget && (
        <RenderEditModal
          projectId={id}
          render={renderEditTarget}
          imageUrl={resolveApiFileUrl(renderEditTarget.image_url)}
          onSaved={rememberSavedRender}
          onClose={() => setRenderEditTarget(null)}
        />
      )}
    </div>
  );
}

interface ProjectRendersTrayProps {
  renders: SavedRender[];
  videos: VideoAttempt[];
  open: boolean;
  onToggle: () => void;
  onClose: () => void;
  onSelect: (render: SavedRender) => void;
  onSelectVideo: (video: VideoAttempt) => void;
}

function RenderSourceNote({ render }: { render: SavedRender }) {
  return <p className="mt-2 text-xs text-white/90">
    {savedRenderNotice(render)}
    {render.provenance_url && <a href={resolveApiFileUrl(render.provenance_url)} target="_blank" rel="noreferrer"
      className="ml-2 inline-flex min-h-8 items-center underline">View source record</a>}
  </p>;
}

function videoDownloadUrl(video: VideoAttempt): string {
  const source = resolveApiFileUrl(video.video_url ?? '');
  const separator = source.includes('?') ? '&' : '?';
  const provider = video.provider === 'seedance_mini'
    ? 'seedance-mini'
    : video.provider === 'internal_enhance'
      ? 'internal-enhance'
      : 'omni';
  const name = `city-prompt-${provider}-${video.style}-${video.camera_motion}-${video.id.slice(0, 8)}.mp4`;
  return `${source}${separator}download=true&filename=${encodeURIComponent(name)}`;
}

function videoProviderOrigin(video: VideoAttempt): string {
  if (video.provider === 'seedance_mini') return 'Seedance Mini';
  if (video.provider === 'internal_enhance') return 'City Prompt local pipeline';
  return 'Gemini Omni';
}

function videoRenderLabel(video: VideoAttempt): string {
  const motion = video.camera_motion.split('_').join(' ');
  const provider = video.provider === 'seedance_mini'
    ? 'Seedance Mini'
    : video.provider === 'internal_enhance'
      ? 'Internal Enhance'
      : 'Omni';
  const reference = video.provider === 'seedance_mini'
    ? video.seedance_reference_mode === 'preview_plus_keyframes' ? 'preview + 3 views' : 'preview only'
    : video.provider === 'internal_enhance'
      ? 'source-locked cleanup'
    : 'source fidelity';
  if (video.style === 'source_fidelity') return `${provider} · ${reference} · ${motion}`;
  return `${provider} · ${video.style.split(/[_-]/).join(' ')} · ${motion}`;
}

function ProjectRendersTray({ renders, videos, open, onToggle, onClose, onSelect, onSelectVideo }: ProjectRendersTrayProps) {
  const [showAiAttempts, setShowAiAttempts] = useState(true);
  const attemptCount = renders.filter((render) => render.variant === 'provider_original').length;
  const items = [
    ...renders.filter((render) => showAiAttempts || render.variant !== 'provider_original')
      .map((render) => ({ kind: 'image' as const, created_at: render.created_at, render })),
    ...videos.map((video) => ({ kind: 'video' as const, created_at: video.created_at, video })),
  ].sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime());

  if (!open) {
    return (
      <button
        type="button"
        onClick={onToggle}
        className="absolute bottom-3 left-3 z-30 flex items-center gap-2 rounded-lg bg-gray-900/90 px-3 py-2 text-sm font-semibold text-white shadow-lg backdrop-blur-sm transition hover:bg-gray-800/95"
        title="Open project renders"
      >
        <Camera size={16} className="text-amber-300" />
        Project Renders
        <span className="rounded-full bg-white/15 px-2 py-0.5 text-xs text-white/80">{items.length}</span>
      </button>
    );
  }

  return (
    <div className="absolute bottom-3 left-3 z-40 flex max-h-[min(28rem,calc(100%-1.5rem))] w-[22rem] max-w-[calc(100%-1.5rem)] flex-col overflow-hidden rounded-xl bg-white/95 shadow-2xl ring-1 ring-black/10 backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-primary-950/[0.08] px-4 py-3">
        <div>
          <h3 className="text-sm font-bold text-primary-950">Project Renders</h3>
          <p className="text-xs text-primary-950/50">{items.length} saved in this project</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="flex items-center gap-1.5 rounded-lg border border-primary-950/[0.12] px-2.5 py-1.5 text-xs font-semibold text-primary-950/65 transition hover:bg-primary-950/[0.06] hover:text-primary-950"
          aria-label="Close project renders"
        >
          <X size={14} />
          Hide
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {attemptCount > 0 && <label className="mb-3 flex min-h-11 items-center gap-2 text-xs text-slate-700">
          <input type="checkbox" checked={showAiAttempts} onChange={(event) => setShowAiAttempts(event.target.checked)} />
          Show AI originals ({attemptCount})
        </label>}
        {items.length === 0 ? (
          <div className="flex min-h-36 flex-col items-center justify-center rounded-lg border border-dashed border-primary-950/[0.12] px-4 py-6 text-center">
            <Sparkles size={22} className="text-primary-950/25" />
            <p className="mt-2 text-sm font-medium text-primary-950/70">No renders yet</p>
            <p className="mt-1 text-xs text-primary-950/45">New images and videos save here automatically.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {items.map((item) => item.kind === 'image' ? (
              <button key={`image-${item.render.id}`} type="button" onClick={() => onSelect(item.render)} className="group relative overflow-hidden rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.03] text-left transition hover:border-amber-400/80">
                <img src={resolveApiFileUrl(item.render.image_url)} alt={item.render.prompt || 'Saved render'} className="aspect-square w-full object-cover" />
                {savedRenderNeedsReview(item.render) && <span className="absolute left-1 top-1 rounded bg-amber-100 px-1.5 py-1 text-[10px] font-bold text-amber-950">
                  {item.render.variant === 'provider_original' ? 'AI render' : savedRenderIsSource(item.render) ? '3D source' : 'Compare with plan'}
                </span>}
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/75 to-transparent p-2 opacity-0 transition group-hover:opacity-100">
                  <p className="truncate text-[10px] font-semibold text-white">{item.render.style || 'render'}</p>
                  <p className="text-[10px] text-white/65">{new Date(item.render.created_at).toLocaleDateString()}</p>
                </div>
              </button>
            ) : (
              <button key={`video-${item.video.id}`} type="button" onClick={() => onSelectVideo(item.video)} className="group relative overflow-hidden rounded-lg border border-primary-950/[0.08] bg-black text-left transition hover:border-[#28c7e8]">
                {item.video.guide_image_url ? (
                  <img src={resolveApiFileUrl(item.video.guide_image_url)} alt="Video flight path" className="aspect-square w-full object-cover opacity-80" />
                ) : (
                  <div className="aspect-square w-full bg-[#0d1718]" />
                )}
                <div className="absolute inset-0 flex items-center justify-center bg-black/15 transition group-hover:bg-black/30">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-[#151515] shadow-lg"><Video size={19} fill="currentColor" /></span>
                </div>
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 to-transparent p-2">
                  <p className="truncate text-[10px] font-semibold capitalize text-white">{videoRenderLabel(item.video)} · video</p>
                  <p className="text-[10px] text-white/65">{new Date(item.video.created_at).toLocaleDateString()}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
