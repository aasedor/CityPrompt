/**
 * GlobeAIRenderPanel.tsx — Simplified AI render controls for the 3D globe.
 *
 * Captures the globe canvas with photorealistic 3D tile context,
 * generates a mask from zone polygons, and sends to Gemini.
 */

import { useState, useCallback, useEffect, useMemo, useRef, type HTMLAttributes, type PointerEvent as ReactPointerEvent } from 'react';
import { createPortal } from 'react-dom';
import * as THREE from 'three';
import { useQueryClient } from '@tanstack/react-query';
import { Boxes, Camera, GripHorizontal, Loader2, Download, X, Check, Image as ImageIcon, Orbit, Trees } from 'lucide-react';
import type { SiteZone, SavedRender } from '@/types';
import { useGlobeAIRender, type GlobeRenderResult, type GlobeRenderProgress, type OpenAIImageQuality, HIGH_FIDELITY_STYLES } from './useGlobeAIRender';
import { rendersApi, resolveApiFileUrl } from '@/services/api';
import { getRenderImageKey, saveRenderedImage } from '@/utils/renderPersistence';
import { isTextEntryTarget } from '@/utils/domEvents';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import {
  buildParkDiagram,
  generateParkGroundTexture,
  getParkGroundMeta,
  MAX_PARK_GROUND_BATCH_CALLS,
  takeParkGroundBatch,
} from './parkGroundTexture';
import {
  resolveCommunity3DAction,
  resolveCommunity3DKind,
  selectCommunity3DCompileZones,
} from '@/features/community3d/community3d';
import { analyzePlanBoundaryAlignment } from '@/features/community3d/planBoundaryAlignment';
import {
  compileMixedCommunity3D,
  deriveItems as deriveCommunityBuildingItems,
} from '@/features/legoAssembly/communityCompiler';
import { estimateCurrentViewRenderCalls } from './renderCost';

// Both preview slots run GPT Image 2 (user verdict 2026-07-07: Gemini globe
// renders consistently weaker; GPT holds the drawn structure best). Two
// samples of one engine give a real A/B choice; labels keep them apart.
const COMPARE_RENDER_MODELS = [
  { model: 'gpt-image-2', label: 'GPT Image 2 · A' },
  { model: 'gpt-image-2', label: 'GPT Image 2 · B' },
];

const DEFAULT_OPENAI_IMAGE_QUALITY: OpenAIImageQuality = 'auto';
const OPENAI_IMAGE_QUALITY_LABELS: Record<OpenAIImageQuality, string> = {
  auto: 'Auto',
  low: 'Low',
  medium: 'Medium',
  high: 'High',
};

function isOpenAIImageModel(model?: string): boolean {
  return Boolean(model?.startsWith('gpt-image-2'));
}

function getQualityForModel(model: string, quality: OpenAIImageQuality): OpenAIImageQuality | undefined {
  return isOpenAIImageModel(model) ? quality : undefined;
}

function formatImageQualityLabel(quality?: OpenAIImageQuality): string | null {
  if (!quality) return null;
  return `GPT ${OPENAI_IMAGE_QUALITY_LABELS[quality] ?? quality}`;
}

function getLightboxMetaParts(render: LightboxRender): string[] {
  const qualityLabel = formatImageQualityLabel(render.imageQuality);
  return [
    render.providerLabel,
    qualityLabel && !render.style?.includes(qualityLabel) ? qualityLabel : null,
    render.style,
    render.createdAt ? new Date(render.createdAt).toLocaleDateString() : null,
  ].filter(Boolean) as string[];
}

interface GlobeAIRenderPanelProps {
  canvas: HTMLCanvasElement | null;
  camera: THREE.Camera | null;
  siteZones: SiteZone[];
  terrainHeight: number;
  projectId?: string;
  /** Currently selected map zone; enables a one-park paid drape action. */
  selectedZoneId?: string | null;
  /** Buildings whose detailed model or exact-footprint massing is placed. */
  modeledBuildingIds?: Set<string>;
  /** Hide/show placed models — used for polygon-only captures. */
  setBuildingModelsVisible?: (visible: boolean) => void;
  onRenderComplete?: (result: GlobeRenderResult) => void;
  onBeforeRender?: () => void | Promise<void>;
  dragHandleProps?: HTMLAttributes<HTMLDivElement>;
  isDragging?: boolean;
  onLightboxOpenChange?: (open: boolean) => void;
  onRenderSaved?: (render: SavedRender) => void;
  onClose?: () => void;
}

const STYLES = [
  // ── Realistic — photo-style final-stage visualization ──
  { id: 'photorealistic', label: 'Photo Realistic' },
  { id: 'photomontage', label: 'Photomontage' },
  { id: 'development', label: 'Development' },
  { id: 'atmospheric', label: 'Atmospheric' },
  { id: 'winter', label: 'Winter' },
  { id: 'night', label: 'Night' },
  // ── Concept — hand-drawn / painterly early-stage exploration ──
  { id: 'watercolour', label: 'Watercolour' },
  { id: 'charcoal', label: 'Charcoal' },
  { id: 'marker-render', label: 'Marker' },
  { id: 'pen-and-ink', label: 'Pen & Ink' },
  // ── Accurate — geometry-faithful architectural photography ──
  { id: 'survey', label: 'Survey' },
  { id: 'documentary', label: 'Documentary' },
  // ── Plan — top-down orthographic / drafted planning views ──
  { id: 'site-plan', label: 'Site Plan' },
  { id: 'site-plan-photo', label: 'Site Plan Photo' },
  { id: 'blueprint', label: 'Blueprint' },
  { id: 'site-plan-watercolor', label: 'Site Plan WC' },
  // ── Stylized — bold, graphic, distinctive ──
  { id: 'isometric', label: 'Isometric' },
  { id: 'clay-maquette', label: 'Clay' },
  { id: 'woodblock', label: 'Wood Block' },
  { id: 'collage', label: 'Collage' },
  { id: 'risograph', label: 'Risograph' },
  { id: 'pixel-art', label: 'Pixel Art' },
] as const;

// UI grouping for the style picker — keeps the new-user taxonomy visible.
// Update this when adding a style so it lands in the right group in the UI.
const STYLE_GROUPS = [
  { label: 'Realistic', ids: ['photorealistic', 'photomontage', 'development', 'atmospheric', 'winter', 'night'] },
  { label: 'Accurate', ids: ['survey', 'documentary'] },
  { label: 'Concept', ids: ['watercolour', 'charcoal', 'marker-render', 'pen-and-ink'] },
  { label: 'Plan', ids: ['site-plan', 'site-plan-photo', 'blueprint', 'site-plan-watercolor'] },
  { label: 'Stylized', ids: ['isometric', 'clay-maquette', 'woodblock', 'collage', 'risograph', 'pixel-art'] },
] as const;

type LightboxRender = {
  imageUrl: string;
  prompt?: string;
  style?: string;
  seed?: number;
  model?: string;
  imageQuality?: OpenAIImageQuality;
  providerLabel?: string;
  savedRenderId?: string;
  createdAt?: string;
  downloadName: string;
  canSave?: boolean;
};

export function GlobeAIRenderPanel({
  canvas,
  camera,
  siteZones,
  terrainHeight,
  projectId,
  selectedZoneId,
  modeledBuildingIds,
  setBuildingModelsVisible,
  onRenderComplete,
  onBeforeRender,
  dragHandleProps,
  isDragging = false,
  onLightboxOpenChange,
  onRenderSaved,
  onClose,
}: GlobeAIRenderPanelProps) {
  const { renderPreviews } = useGlobeAIRender();
  const queryClient = useQueryClient();
  const [isRendering, setIsRendering] = useState(false);
  const [isPreparingCapture, setIsPreparingCapture] = useState(false);
  const [result, setResult] = useState<GlobeRenderResult | null>(null);
  const [previews, setPreviews] = useState<GlobeRenderResult[]>([]);
  const [selectedPreviewIndex, setSelectedPreviewIndex] = useState<number | null>(null);
  const [selectedStyle, setSelectedStyle] = useState('photorealistic');
  const [customPrompt, setCustomPrompt] = useState('');
  const [highFidelity, setHighFidelity] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Development mode gate: at least one zone in the scene is backed by real
  // massing (placed LEGO stack or mounted 3D model) that the capture shows.
  const hasPlacedMassing = useMemo(
    () => Boolean(modeledBuildingIds?.size)
      && siteZones.some((z) => z.building_id && modeledBuildingIds?.has(z.building_id)),
    [siteZones, modeledBuildingIds],
  );
  useEffect(() => {
    if (selectedStyle === 'development' && !hasPlacedMassing) setSelectedStyle('photorealistic');
  }, [selectedStyle, hasPlacedMassing]);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved' | 'error'>('idle');
  const [savedRenders, setSavedRenders] = useState<SavedRender[]>([]);
  const [showSavedRenders, setShowSavedRenders] = useState(false);
  const [renderTime, setRenderTime] = useState(0);
  const [renderProgress, setRenderProgress] = useState<GlobeRenderProgress | null>(null);
  // Lightbox: render currently shown full-screen (null = closed).
  const [lightboxRender, setLightboxRender] = useState<LightboxRender | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const savedImageKeysRef = useRef<Set<string>>(new Set());

  // ── 3D building models ──
  // When ON (default) placed models stay in the capture and their zones get
  // preserve-the-massing prompts — geometry-conditioned accuracy. OFF hides
  // the models for the capture (classic polygon-only behavior).
  const [renderWithModels, setRenderWithModels] = useState(true);
  const [confirm3DOpen, setConfirm3DOpen] = useState(false);
  const [isQueuing3D, setIsQueuing3D] = useState(false);
  const [generate3DStatus, setGenerate3DStatus] = useState<string | null>(null);
  const renderCallCount = estimateCurrentViewRenderCalls(
    COMPARE_RENDER_MODELS.length,
    highFidelity && HIGH_FIDELITY_STYLES.has(selectedStyle),
  );

  const boundaryZone3D = siteZones.find(
    (z) => z.zone_type === 'site_boundary' && z.coordinates.length >= 3,
  );
  const buildableZones = useMemo(
    () => deriveCommunityBuildingItems(siteZones)
      .map((item) => item.zone)
      .filter((zone) => (
        (zone.properties as Record<string, unknown> | undefined)?._plan_role !== 'framework_height'
      )),
    [siteZones],
  );
  const communityGroundZones = useMemo(
    () => siteZones.filter((z) => {
      const kind = resolveCommunity3DKind(z);
      return (kind === 'park' || kind === 'street') && z.coordinates.length >= 3;
    }),
    [siteZones],
  );
  const communityZones = useMemo(
    () => [...buildableZones, ...communityGroundZones],
    [buildableZones, communityGroundZones],
  );
  const community3DAction = resolveCommunity3DAction(communityZones);
  const communityCompileZones = useMemo(
    () => selectCommunity3DCompileZones(communityZones, community3DAction),
    [community3DAction, communityZones],
  );
  const communityCompileBuildingCount = communityCompileZones.filter(
    (zone) => resolveCommunity3DKind(zone) === 'building',
  ).length;
  const communityCompileParkCount = communityCompileZones.filter(
    (zone) => resolveCommunity3DKind(zone) === 'park',
  ).length;
  const communityCompileStreetCount = communityCompileZones.filter(
    (zone) => resolveCommunity3DKind(zone) === 'street',
  ).length;
  const community3DActionLabel = community3DAction === 'rebuild'
    ? 'Rebuild'
    : community3DAction === 'complete'
      ? 'Complete'
      : 'Generate';
  const unsavedCommunityCount = communityZones
    .filter((z) => !isPersistedZoneId(z.id)).length;
  const planBoundaryAlignment = useMemo(
    () => analyzePlanBoundaryAlignment(siteZones),
    [siteZones],
  );
  const planGeometryStale = !planBoundaryAlignment.isAligned;
  const stalePlanMessage = planGeometryStale
    ? planBoundaryAlignment.boundary === null && planBoundaryAlignment.requiresBoundary
      ? `${planBoundaryAlignment.planZones.length} generated plan zones are missing their saved site boundary. Restore or redraw the master plan before generating 3D or renders.`
      : `${planBoundaryAlignment.misalignedZones.length} of ${planBoundaryAlignment.planZones.length} generated plan zones no longer fit the current site boundary. Redraw the master plan before spending credits on 3D or renders.`
    : null;
  const boundaryPersisted = Boolean(boundaryZone3D && isPersistedZoneId(boundaryZone3D.id));
  const communityBoundaryReady = !planBoundaryAlignment.requiresBoundary || boundaryPersisted;
  const canGenerate3D = Boolean(
    projectId
    && communityBoundaryReady
    && !planGeometryStale
    && communityZones.length > 0
    && unsavedCommunityCount === 0,
  );

  // ── Park ground textures (AI ortho drape; one Gemini render per park) ──
  const [isGeneratingParks, setIsGeneratingParks] = useState(false);
  const [parkGroundStatus, setParkGroundStatus] = useState<string | null>(null);
  const parkZones = siteZones.filter(
    (z) => resolveCommunity3DKind(z) === 'park'
      && z.coordinates.length >= 3
      && isPersistedZoneId(z.id),
  );
  const parksNeedingGround = parkZones.filter((z) => !getParkGroundMeta(z));
  const parkGroundBatch = takeParkGroundBatch(parksNeedingGround);
  const selectedParkNeedingGround = parksNeedingGround.find((z) => z.id === selectedZoneId) ?? null;
  const parkEligibleForGroundRegeneration = (
    parkZones.find((z) => z.id === selectedZoneId)
    ?? (parkZones.length === 1 ? parkZones[0] : null)
  );
  const parkHasGroundToRegenerate = parkEligibleForGroundRegeneration
    && getParkGroundMeta(parkEligibleForGroundRegeneration)
    ? parkEligibleForGroundRegeneration
    : null;

  const handleGenerateSelectedParkGround = useCallback(async () => {
    if (planGeometryStale || isGeneratingParks || !selectedParkNeedingGround) return;
    const label = selectedParkNeedingGround.name || 'selected park';
    setIsGeneratingParks(true);
    setParkGroundStatus(`Generating optional AI material drape for ${label}…`);
    setError(null);
    try {
      await generateParkGroundTexture(selectedParkNeedingGround);
      setParkGroundStatus(`Generated optional AI material drape for ${label}.`);
      await queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      await queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not generate the selected park ground.');
      setParkGroundStatus(null);
    } finally {
      setIsGeneratingParks(false);
    }
  }, [isGeneratingParks, planGeometryStale, projectId, queryClient, selectedParkNeedingGround]);

  const handleRegenerateParkGround = useCallback(async () => {
    if (planGeometryStale || isGeneratingParks || !parkHasGroundToRegenerate) return;
    const label = parkHasGroundToRegenerate.name || 'selected park';
    setIsGeneratingParks(true);
    setParkGroundStatus(`Regenerating geometry-locked AI material drape for ${label}…`);
    setError(null);
    try {
      await generateParkGroundTexture(parkHasGroundToRegenerate);
      setParkGroundStatus(`Regenerated geometry-locked AI material drape for ${label}.`);
      await queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      await queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not regenerate the selected park ground.');
      setParkGroundStatus(null);
    } finally {
      setIsGeneratingParks(false);
    }
  }, [isGeneratingParks, parkHasGroundToRegenerate, planGeometryStale, projectId, queryClient]);

  const handleGenerateParkGrounds = useCallback(async () => {
    if (planGeometryStale || isGeneratingParks || parksNeedingGround.length === 0) return;
    setIsGeneratingParks(true);
    setParkGroundStatus(
      `Generating optional AI park-ground upgrades… 0/${parkGroundBatch.length} (${parksNeedingGround.length} eligible)`,
    );
    setError(null);
    let done = 0;
    let failed = 0;
    // Sequential on purpose: each call is a full Gemini render; parallel
    // fan-out would trip the proxy's daily token cap alarms for no benefit.
    for (const zone of parkGroundBatch) {
      try {
        await generateParkGroundTexture(zone);
        done += 1;
      } catch (err) {
        failed += 1;
        console.warn('[parkGrounds] generation failed for zone', zone.id, err);
      }
      setParkGroundStatus(
        `Generating optional AI park-ground upgrades… ${done + failed}/${parkGroundBatch.length}`,
      );
      // Refresh zones as textures land so the globe drapes them immediately.
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    }
    const remaining = Math.max(0, parksNeedingGround.length - done);
    setParkGroundStatus(
      `${done} AI park-ground upgrade${done === 1 ? '' : 's'} generated${failed ? `, ${failed} failed` : ''}.`
      + (remaining > 0 ? ` ${remaining} parks still use their complete procedural grounds; start another optional batch explicitly.` : ''),
    );
    setIsGeneratingParks(false);
  }, [
    planGeometryStale,
    isGeneratingParks,
    parkGroundBatch,
    parksNeedingGround.length,
    queryClient,
    projectId,
  ]);

  // DEV pilot hook: regenerate the ground texture for ONE park by zone id
  // (the panel button only fills MISSING textures, so per-zone pilots can't
  // use it). Returns the conditioning diagram + marker counts + stored meta.
  useEffect(() => {
    if (!import.meta.env.DEV) return undefined;
    const dbg = ((window as unknown as Record<string, unknown>).__globeDebug ??= {}) as Record<string, unknown>;
    dbg.generateParkGround = async (zoneId: string) => {
      const zone = siteZones.find((z) => z.id === zoneId);
      if (!zone) throw new Error(`zone ${zoneId} not loaded`);
      const diagram = buildParkDiagram(zone);
      const meta = await generateParkGroundTexture(zone);
      queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
      return { diagram: diagram?.dataUrl, markers: diagram?.markers, meta };
    };
    return () => {
      delete dbg.generateParkGround;
    };
  }, [siteZones, queryClient, projectId]);

  const handleGenerate3D = useCallback(async () => {
    if (planGeometryStale || !projectId || !communityBoundaryReady || isQueuing3D) return;
    setIsQueuing3D(true);
    setGenerate3DStatus(null);
    setError(null);
    try {
      const summary = await compileMixedCommunity3D(
        communityCompileZones,
        ({ completed, total }) => {
          setGenerate3DStatus(
            total > 0
              ? `Preparing modular buildings… ${completed}/${total}`
              : 'Compiling parks and streets…',
          );
        },
      );
      setGenerate3DStatus(
        `Built ${summary.detailedBuildings} detailed modular building${summary.detailedBuildings === 1 ? '' : 's'}, `
        + `${summary.plannedMasses} family-pending exact mass${summary.plannedMasses === 1 ? '' : 'es'}, `
        + `${summary.parks} park${summary.parks === 1 ? '' : 's'}, and `
        + `${summary.streets} street/path layer${summary.streets === 1 ? '' : 's'}.`,
      );
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['project', projectId] }),
        queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] }),
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to build the mixed 3D community');
    } finally {
      setIsQueuing3D(false);
      setConfirm3DOpen(false);
    }
  }, [planGeometryStale, projectId, communityBoundaryReady, isQueuing3D, communityCompileZones, queryClient]);

  useEffect(() => {
    onLightboxOpenChange?.(!!lightboxRender);
    return () => onLightboxOpenChange?.(false);
  }, [lightboxRender, onLightboxOpenChange]);

  const refreshSavedRenders = useCallback(async () => {
    if (!projectId) {
      setSavedRenders([]);
      return;
    }
    try {
      setSavedRenders(await rendersApi.list(projectId));
    } catch {
      // The gallery is supplemental; render controls should stay usable.
    }
  }, [projectId]);

  useEffect(() => {
    refreshSavedRenders();
  }, [refreshSavedRenders]);

  useEffect(() => {
    setSaveStatus('idle');
  }, [result?.imageUrl]);

  const rememberSavedRender = useCallback((saved: SavedRender) => {
    setSavedRenders((prev) => [saved, ...prev.filter((r) => r.id !== saved.id)]);
    onRenderSaved?.(saved);
  }, [onRenderSaved]);

  const autoSaveGlobeRenders = useCallback(async (rendersToSave: GlobeRenderResult[]) => {
    if (!projectId) return false;
    const unsaved = rendersToSave
      .filter((renderToSave) => !renderToSave.error && renderToSave.imageUrl)
      .map((renderToSave) => ({
        render: renderToSave,
        key: getRenderImageKey(renderToSave),
      }))
      .filter(({ key }) => {
        if (savedImageKeysRef.current.has(key)) return false;
        savedImageKeysRef.current.add(key);
        return true;
      });

    if (unsaved.length === 0) return false;

    const results = await Promise.allSettled(
      unsaved.map(({ render }) => saveRenderedImage(
        projectId,
        render,
        render.providerLabel
          ? [render.providerLabel, formatImageQualityLabel(render.imageQuality), selectedStyle].filter(Boolean).join(' / ')
          : selectedStyle,
      )),
    );

    results.forEach((saveResult, index) => {
      if (saveResult.status === 'rejected') {
        savedImageKeysRef.current.delete(unsaved[index].key);
      }
    });

    const saved = results
      .filter((saveResult): saveResult is PromiseFulfilledResult<SavedRender> => saveResult.status === 'fulfilled')
      .map((saveResult) => saveResult.value);

    if (saved.length === 0) return false;
    setSavedRenders((prev) => [
      ...saved,
      ...prev.filter((item) => !saved.some((savedRender) => savedRender.id === item.id)),
    ]);
    saved.forEach((savedRender) => onRenderSaved?.(savedRender));
    setShowSavedRenders(true);
    return true;
  }, [onRenderSaved, projectId, selectedStyle]);

  const handleRender = useCallback(async () => {
    if (!canvas || !camera || isRendering) return;

    if (planGeometryStale) {
      setError(stalePlanMessage ?? 'Redraw the master plan for the current site boundary before rendering.');
      return;
    }

    const editableZones = siteZones.filter(z =>
      z.zone_type !== 'site_boundary' && z.coordinates.length >= 3
    );
    // Threaded separately so the post-render clip can intersect ground zones
    // with the site boundary (building hulls exempt) — see clipRenderToZones.
    const siteBoundaryZone = siteZones.find(z =>
      z.zone_type === 'site_boundary' && z.coordinates.length >= 3
    );

    if (editableZones.length === 0) {
      setError('Draw some zones first before rendering');
      return;
    }

    setIsRendering(true);
    setIsPreparingCapture(true);
    setResult(null);
    setPreviews([]);
    setSelectedPreviewIndex(null);
    setError(null);
    setRenderProgress(null);
    const startTime = Date.now();
    const timer = setInterval(() => setRenderTime(Math.round((Date.now() - startTime) / 1000)), 1000);
    let hidModels = false;

    try {
      // Do not spend image credits against a half-streamed Google scene.
      // The parent waits for a stable tile window and throws on its bounded
      // timeout; this catch then returns the user to an idle, retryable state.
      await onBeforeRender?.();
      setIsPreparingCapture(false);

      // 3D models in the capture: when the toggle is OFF, hide the placed GLBs
      // for the screenshot (classic polygon-only conditioning) and restore
      // after. When ON, pass the modeled ids so those zones get
      // preserve-the-massing prompts instead of replace-the-polygon.
      const includeModels = renderWithModels && (modeledBuildingIds?.size ?? 0) > 0;
      hidModels = !includeModels && (modeledBuildingIds?.size ?? 0) > 0 && !!setBuildingModelsVisible;
      if (hidModels) {
        setBuildingModelsVisible!(false);
        // Let R3F unmount the layer and repaint (prisms return) before capture.
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
      const renderModeledIds = includeModels ? modeledBuildingIds : undefined;

      // Current-view rendering is deliberately bounded to one A/B single-shot
      // batch. Per-zone generation must never be selected automatically: a
      // district plan could otherwise fan out into hundreds of paid calls.
      const compareRenderVariants = COMPARE_RENDER_MODELS.map((provider) => ({
        ...provider,
        imageQuality: getQualityForModel(provider.model, DEFAULT_OPENAI_IMAGE_QUALITY),
      }));
      // Fan out the two bounded previews with different server seeds. The
      // first success is auto-selected; the user can compare the other.
      const results = await renderPreviews(canvas, camera, editableZones, terrainHeight, {
        style: selectedStyle,
        projectId,
        customPrompt: customPrompt.trim() || undefined,
        siteBoundaryZone,
        highFidelity,
        modeledBuildingIds: renderModeledIds,
        variants: compareRenderVariants,
      });
      if (results.length > 0) {
        setPreviews(results);
        const firstSuccessfulIndex = Math.max(0, results.findIndex((preview) => !preview.error));
        const selected = results[firstSuccessfulIndex];
        setSelectedPreviewIndex(firstSuccessfulIndex);
        setResult(selected);
        const savedAny = await autoSaveGlobeRenders(results);
        if (!selected.error) {
          onRenderComplete?.(selected);
        }
        if (savedAny) {
          onClose?.();
        }
        const failedLabels = results.filter((preview) => preview.error).map((preview) => preview.providerLabel || preview.model);
        if (failedLabels.length > 0) {
          setError(`${failedLabels.join(', ')} failed. Open the labeled preview for details.`);
        }
      } else {
        setError('Render returned no image. Try adjusting your view or zones.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Render failed. Please try again.');
    } finally {
      clearInterval(timer);
      setRenderTime(0);
      setRenderProgress(null);
      setIsPreparingCapture(false);
      setIsRendering(false);
      if (hidModels) setBuildingModelsVisible!(true);
    }
  }, [canvas, camera, siteZones, terrainHeight, selectedStyle, isRendering, renderPreviews, projectId, onRenderComplete, onBeforeRender, customPrompt, highFidelity, autoSaveGlobeRenders, onClose, renderWithModels, modeledBuildingIds, setBuildingModelsVisible, planGeometryStale, stalePlanMessage]);

  // Close lightbox on Esc
  useEffect(() => {
    if (!lightboxRender) return;
    const onKey = (e: KeyboardEvent) => {
      if (isTextEntryTarget(e.target)) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        setLightboxRender(null);
      }
    };
    window.addEventListener('keydown', onKey, true);
    return () => window.removeEventListener('keydown', onKey, true);
  }, [lightboxRender]);

  const handleSelectPreview = useCallback((index: number) => {
    if (index < 0 || index >= previews.length) return;
    const selected = previews[index];
    setSelectedPreviewIndex(index);
    setResult(selected);
    setLightboxRender((current) => current
      ? {
          ...current,
          imageUrl: selected.imageUrl,
          prompt: selected.error || selected.prompt,
          style: [formatImageQualityLabel(selected.imageQuality), selectedStyle].filter(Boolean).join(' / '),
          seed: selected.seed,
          providerLabel: selected.providerLabel,
          model: selected.model,
          imageQuality: selected.imageQuality,
          downloadName: `siteforge-globe-${selected.providerLabel || `preview-${index + 1}`}-${Date.now()}.png`,
          canSave: Boolean(projectId) && !selected.error,
        }
      : current);
    if (!selected.error) {
      onRenderComplete?.(selected);
    }
  }, [previews, onRenderComplete, projectId, selectedStyle]);

  const handleStepPreview = useCallback((direction: -1 | 1) => {
    if (previews.length < 2) return;
    const currentIndex = selectedPreviewIndex ?? 0;
    const nextIndex = (currentIndex + direction + previews.length) % previews.length;
    handleSelectPreview(nextIndex);
  }, [handleSelectPreview, previews.length, selectedPreviewIndex]);

  useEffect(() => {
    if (previews.length < 2 || isRendering || lightboxRender?.savedRenderId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      if (isTextEntryTarget(e.target)) return;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      handleStepPreview(e.key === 'ArrowRight' ? 1 : -1);
    };
    window.addEventListener('keydown', onKey, true);
    return () => window.removeEventListener('keydown', onKey, true);
  }, [handleStepPreview, isRendering, lightboxRender?.savedRenderId, previews.length]);

  const handleDownload = useCallback(() => {
    if (!result?.imageUrl || result.error) return;
    const providerSlug = (result.providerLabel || 'render').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const a = document.createElement('a');
    a.href = result.imageUrl;
    a.download = `siteforge-globe-${providerSlug}-${Date.now()}.png`;
    a.click();
  }, [result]);

  const saveRenderToProject = useCallback(async (renderToSave: Pick<LightboxRender, 'imageUrl' | 'prompt' | 'style' | 'seed' | 'providerLabel' | 'model' | 'imageQuality'>) => {
    if (!renderToSave.imageUrl || !projectId || saving) return;
    setSaving(true);
    setSaveStatus('idle');
    try {
      const saved = await saveRenderedImage(
        projectId,
        renderToSave,
        renderToSave.providerLabel
          ? [renderToSave.providerLabel, formatImageQualityLabel(renderToSave.imageQuality), renderToSave.style || selectedStyle].filter(Boolean).join(' / ')
          : renderToSave.style || selectedStyle,
      );
      savedImageKeysRef.current.add(getRenderImageKey(renderToSave));
      rememberSavedRender(saved);
      setShowSavedRenders(true);
      setSaveStatus('saved');
      setLightboxRender((current) => current?.imageUrl === renderToSave.imageUrl
        ? {
            ...current,
            prompt: saved.prompt || current.prompt,
            style: saved.style || current.style,
            model: saved.model || current.model,
            imageQuality: saved.image_quality || current.imageQuality,
            createdAt: saved.created_at,
            downloadName: `render-${saved.id}.png`,
          }
        : current);
    } catch {
      setSaveStatus('error');
    } finally {
      setSaving(false);
    }
  }, [projectId, rememberSavedRender, selectedStyle, saving]);

  const handleSave = useCallback(async () => {
    if (!result?.imageUrl || result.error) return;
    await saveRenderToProject({
      imageUrl: result.imageUrl,
      prompt: result.prompt,
      style: selectedStyle,
      seed: result.seed,
      providerLabel: result.providerLabel,
      model: result.model,
      imageQuality: result.imageQuality,
    });
  }, [result, saveRenderToProject, selectedStyle]);

  const openResultLightbox = useCallback((renderResult: GlobeRenderResult, label: string) => {
    setLightboxRender({
      imageUrl: renderResult.imageUrl,
      prompt: renderResult.prompt,
      style: [formatImageQualityLabel(renderResult.imageQuality), selectedStyle].filter(Boolean).join(' / '),
      seed: renderResult.seed,
      model: renderResult.model,
      imageQuality: renderResult.imageQuality,
      providerLabel: renderResult.providerLabel,
      downloadName: `${label}-${Date.now()}.png`,
      canSave: Boolean(projectId),
    });
  }, [projectId, selectedStyle]);

  const openSavedRenderLightbox = useCallback((saved: SavedRender) => {
    setLightboxRender({
      imageUrl: resolveApiFileUrl(saved.image_url),
      prompt: saved.prompt,
      style: saved.style,
      model: saved.model,
      imageQuality: saved.image_quality,
      createdAt: saved.created_at,
      savedRenderId: saved.id,
      downloadName: `render-${saved.id}.png`,
      canSave: false,
    });
  }, []);

  const handleStepSavedRender = useCallback((direction: -1 | 1) => {
    const savedRenderId = lightboxRender?.savedRenderId;
    if (!savedRenderId || savedRenders.length < 2) return;
    const currentIndex = savedRenders.findIndex((saved) => saved.id === savedRenderId);
    const startIndex = currentIndex >= 0 ? currentIndex : 0;
    const nextIndex = (startIndex + direction + savedRenders.length) % savedRenders.length;
    openSavedRenderLightbox(savedRenders[nextIndex]);
  }, [lightboxRender?.savedRenderId, openSavedRenderLightbox, savedRenders]);

  useEffect(() => {
    if (!lightboxRender?.savedRenderId || savedRenders.length < 2) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      if (isTextEntryTarget(e.target)) return;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      handleStepSavedRender(e.key === 'ArrowRight' ? 1 : -1);
    };
    window.addEventListener('keydown', onKey, true);
    return () => window.removeEventListener('keydown', onKey, true);
  }, [handleStepSavedRender, lightboxRender?.savedRenderId, savedRenders.length]);

  const { className: dragHandleClassName, ...dragHandleRest } = dragHandleProps ?? {};

  const handlePanelPointerMove = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    event.currentTarget.style.setProperty('--globe-ai-x', `${x.toFixed(2)}%`);
    event.currentTarget.style.setProperty('--globe-ai-y', `${y.toFixed(2)}%`);
  }, []);

  const handlePanelPointerLeave = useCallback(() => {
    const panel = panelRef.current;
    if (!panel) return;
    panel.style.setProperty('--globe-ai-x', '50%');
    panel.style.setProperty('--globe-ai-y', '46%');
  }, []);

  return (
    <>
    <div
      ref={panelRef}
      onPointerMove={handlePanelPointerMove}
      onPointerLeave={handlePanelPointerLeave}
      className={`globe-ai-dynamic-bg flex w-full flex-col overflow-hidden rounded-lg border-2 border-[#151515] shadow-[10px_10px_0_0_#151515] backdrop-blur-xl ${isRendering ? 'mx-auto max-h-[13rem] max-w-md globe-ai-rendering' : 'max-h-[44vh]'}`}
    >
      {/* Header */}
      <div
        {...dragHandleRest}
        className={`shrink-0 select-none border-b-2 border-[#151515] bg-[#fff9ec] px-4 py-2.5 ${
          isDragging ? 'cursor-grabbing' : 'cursor-grab'
        } ${dragHandleClassName ?? ''}`}
        title="Drag to move"
      >
        <div className="flex items-center justify-between gap-3">
          <h3 className="flex items-center gap-2 text-sm font-black uppercase text-[#151515]">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg border-2 border-[#151515] bg-[#28c7e8] text-[#151515] shadow-[2px_2px_0_0_#151515]">
              <Orbit size={15} />
            </span>
            Render (Globe)
          </h3>
          <div className="flex items-center gap-2 text-[10px] font-black uppercase text-[#151515]/60">
            <Camera size={12} />
            3D Capture
            <GripHorizontal size={13} className="text-[#151515]/35" />
            {onClose && (
              <button
                onPointerDown={(event) => event.stopPropagation()}
                onClick={(event) => {
                  event.stopPropagation();
                  onClose();
                }}
                className="ml-1 flex h-7 w-7 items-center justify-center rounded-full border-2 border-[#151515] bg-[#ff5a3d] text-white shadow-[2px_2px_0_0_#151515] transition hover:bg-[#ff725c] focus:outline-none focus:ring-2 focus:ring-[#c9ff3d]"
                aria-label="Close AI Render panel"
                title="Close"
              >
                <X size={14} strokeWidth={3} />
              </button>
            )}
          </div>
        </div>
        <p className="mt-1 text-[10px] font-bold text-[#151515]/55">
          Set the globe exactly how you want it. Previews capture the view on screen.
        </p>
      </div>

      {isRendering ? (
        <div className="min-h-0 flex-1 px-4 py-3">
          <div className="flex items-center gap-3 rounded-lg border-2 border-white/15 bg-black/25 px-3 py-2 text-white">
            <Loader2 size={18} className="shrink-0 animate-spin text-[#c9ff3d]" />
            <div className="min-w-0">
              <p className="truncate text-xs font-black uppercase">
                {isPreparingCapture ? 'Preparing detailed Google tiles' : 'Rendering the current globe view'}
              </p>
              <p className="mt-0.5 text-[11px] font-semibold text-white/65">
                {isPreparingCapture
                  ? 'Hold this view still. No image credits are used until the tiles are ready.'
                  : 'You can keep reviewing the map while this runs.'}
              </p>
            </div>
          </div>
        </div>
      ) : (
      <div className="min-h-0 flex-1 overflow-y-auto">
      <div className="border-b-2 border-white/10 px-4 py-2">
        <div className="flex items-start gap-2 rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-[#151515] shadow-[3px_3px_0_0_#151515]">
          <Camera size={15} className="mt-0.5 shrink-0" />
          <div className="min-w-0">
            <p className="text-[11px] font-black uppercase">Current view becomes the render</p>
            <p className="mt-0.5 text-[10px] font-bold leading-snug text-[#151515]/70">
              Pan, zoom, and tilt the globe first. The preview button captures exactly what you see now.
            </p>
          </div>
        </div>
      </div>
      <div className="grid gap-3 border-b-2 border-white/10 px-4 py-2 md:grid-cols-[1.35fr_0.9fr]">
        {/* Style selector */}
        <div>
          <div className="mb-1 text-[10px] font-black uppercase text-white/50">Style</div>
          <div className="space-y-1.5">
            {STYLE_GROUPS.map(group => (
              <div key={group.label}>
                <div className="mb-0.5 text-[9px] font-black uppercase tracking-wider text-white/40">{group.label}</div>
                <div className="flex flex-wrap gap-1">
                  {group.ids.map(id => {
                    const s = STYLES.find(x => x.id === id);
                    if (!s) return null;
                    // Development mode conditions on real massing in the
                    // capture — meaningless until a LEGO stack or 3D model is
                    // placed on some zone in the scene.
                    const needsPlacedMassing = s.id === 'development';
                    const disabled = needsPlacedMassing && !hasPlacedMassing;
                    return (
                      <button
                        key={s.id}
                        onClick={() => setSelectedStyle(s.id)}
                        disabled={disabled}
                        title={disabled
                          ? 'Development mode needs placed 3D massing — use the LEGO Builder’s Place button (or place a generated model) first.'
                          : s.id === 'development'
                            ? 'High-fidelity render of the placed development: the textured stacks in view act as geometry conditioning.'
                            : undefined}
                        className={`rounded-full border px-2 py-1 text-[11px] font-black transition ${
                          selectedStyle === s.id
                            ? 'border-[#151515] bg-[#c9ff3d] text-[#151515] shadow-[2px_2px_0_0_#151515]'
                            : disabled
                              ? 'cursor-not-allowed border-white/10 bg-white/5 text-white/30'
                              : 'border-white/15 bg-white/10 text-white/70 hover:bg-white/20 hover:text-white'
                        }`}
                      >
                        {s.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* High-fidelity two-pass toggle — camera-preserving artistic styles only */}
        {HIGH_FIDELITY_STYLES.has(selectedStyle) && (
          <label className="flex cursor-pointer items-center gap-2 text-[11px] font-bold text-white/70">
            <input
              type="checkbox"
              checked={highFidelity}
              onChange={(e) => setHighFidelity(e.target.checked)}
              className="h-3.5 w-3.5 accent-[#c9ff3d]"
            />
            High fidelity (+1 shared restyle call) — restyles the whole frame first, then paints the
            zones onto it so there is no style seam
          </label>
        )}

        {/* Custom prompt */}
        <div>
          <div className="mb-1 text-[10px] font-black uppercase text-white/50">Prompt</div>
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Additional instructions (optional)..."
            rows={2}
            className="w-full resize-none rounded-lg border-2 border-white/15 bg-white/5 px-3 py-2 text-xs font-semibold text-white placeholder-white/35 focus:border-[#c9ff3d] focus:outline-none"
          />
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="px-4 py-2">
          <div className="rounded-lg border-2 border-[#ff5a3d] bg-red-500/20 px-3 py-2 text-xs font-bold text-red-200">
            {error}
          </div>
        </div>
      )}

      {/* Preview grid (only when multiple previews exist) */}
      {previews.length > 1 && (
        <div className="px-4 pb-2">
          <div className="mb-1 flex items-center justify-between text-[10px] text-gray-400">
            <span>{selectedPreviewIndex !== null ? previews[selectedPreviewIndex]?.providerLabel || `Preview ${selectedPreviewIndex + 1}` : 'Choose a render'}</span>
            <span>{previews.length} provider test</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {previews.map((p, i) => (
              <button
                key={i}
                onClick={() => {
                  handleSelectPreview(i);
                  if (!p.error) {
                    openResultLightbox(p, `siteforge-globe-${p.providerLabel || `preview-${i + 1}`}`);
                  }
                }}
                className={`relative aspect-video overflow-hidden rounded border-2 transition ${
                  p.error
                    ? 'border-red-400/70 hover:border-red-300'
                    : selectedPreviewIndex === i
                      ? 'border-amber-400 ring-2 ring-amber-400/40'
                      : 'border-white/10 hover:border-white/40'
                }`}
                title={p.error
                  ? `${p.providerLabel || `Preview ${i + 1}`} failed: ${p.error}`
                  : `${p.providerLabel || `Preview ${i + 1}`}${formatImageQualityLabel(p.imageQuality) ? ` / ${formatImageQualityLabel(p.imageQuality)}` : ''}${p.seed !== undefined ? ` (seed ${p.seed})` : ''} - open larger`}
              >
                <img
                  src={p.imageUrl}
                  alt={`${p.providerLabel || `Preview ${i + 1}`} render`}
                  className="h-full w-full object-cover"
                />
                <span className="pointer-events-none absolute left-1 top-1 max-w-[calc(100%-0.5rem)] truncate rounded bg-black/70 px-1.5 py-0.5 text-[10px] font-bold text-white">
                  {[p.providerLabel || `Preview ${i + 1}`, formatImageQualityLabel(p.imageQuality)].filter(Boolean).join(' / ')}
                </span>
                {p.error && (
                  <span className="pointer-events-none absolute bottom-1 left-1 rounded bg-red-500/90 px-1.5 py-0.5 text-[10px] font-bold text-white">
                    Failed
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="px-4 pb-3">
          <div className="relative rounded-lg overflow-hidden border border-white/10">
            {result.providerLabel && (
              <span className="pointer-events-none absolute left-2 top-2 z-10 rounded bg-black/70 px-2 py-1 text-[10px] font-bold text-white">
                {[result.providerLabel, formatImageQualityLabel(result.imageQuality)].filter(Boolean).join(' / ')}
              </span>
            )}
            <img
              src={result.imageUrl}
              alt={`${result.providerLabel || 'AI'} render`}
              className="w-full cursor-zoom-in"
              onClick={() => openResultLightbox(result, 'siteforge-globe-render')}
              title="Click to enlarge"
            />
            <div className="absolute bottom-0 left-0 right-0 flex justify-between items-center bg-gradient-to-t from-black/80 to-transparent px-2 py-1.5">
              {result.error ? (
                <span className="text-[10px] font-medium text-red-200">
                  {result.error}
                </span>
              ) : (
                <>
                  <button
                    onClick={handleSave}
                    disabled={saving || saveStatus === 'saved'}
                    className="flex items-center gap-1 text-[10px] text-white/80 hover:text-white disabled:opacity-70"
                  >
                    {saving && <Loader2 size={10} className="animate-spin" />}
                    {saveStatus === 'saved' && <Check size={10} />}
                    {saving ? 'Saving...' : saveStatus === 'saved' ? 'Saved' : saveStatus === 'error' ? 'Retry save' : 'Save to Project'}
                  </button>
                  <button
                    onClick={handleDownload}
                    className="text-[10px] text-white/80 hover:text-white flex items-center gap-1"
                  >
                    <Download size={10} />
                    Download
                  </button>
                </>
              )}
            </div>
          </div>
          <button
            onClick={() => {
              setResult(null);
              setPreviews([]);
              setSelectedPreviewIndex(null);
            }}
            className="mt-1.5 w-full text-center text-[10px] text-gray-500 hover:text-gray-300"
          >
            Clear result
          </button>
        </div>
      )}

      {/* 3D building models — generate from archetype-assigned zones + render mode */}
      {projectId && communityZones.length > 0 && (
        <div className="border-t-2 border-white/10 px-4 py-3">
          <div className="flex items-center gap-1.5 text-xs font-black uppercase text-white/55">
            <Boxes size={13} />
            Community 3D
          </div>

          {stalePlanMessage && (
            <div className="mt-2 rounded border border-red-400/50 bg-red-500/15 p-2.5 text-[11px] text-red-100">
              <p className="font-black uppercase">Plan boundary changed</p>
              <p className="mt-1 text-red-100/80">{stalePlanMessage}</p>
            </div>
          )}

          {(modeledBuildingIds?.size ?? 0) > 0 && (
            <label className="mt-2 flex cursor-pointer items-center justify-between text-[11px] text-white/70">
              <span>Render with 3D models (geometry-accurate)</span>
              <input
                type="checkbox"
                checked={renderWithModels}
                onChange={(e) => setRenderWithModels(e.target.checked)}
                className="h-3.5 w-3.5 accent-[#c9ff3d]"
              />
            </label>
          )}

          {!confirm3DOpen ? (
            <button
              type="button"
              onClick={() => setConfirm3DOpen(true)}
              disabled={!canGenerate3D || isQueuing3D}
              title={
                planGeometryStale
                  ? stalePlanMessage ?? 'Redraw the master plan for this boundary'
                  : !communityBoundaryReady
                  ? 'Generated master plans require their saved site boundary'
                  : unsavedCommunityCount > 0
                    ? 'Save your zones first — unsaved zones lose their archetype styling'
                    : `${community3DActionLabel} the whole community with modular buildings, exact family-pending massing, parks, and engineered streets`
              }
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border border-white/20 bg-white/5 px-3 py-2 text-[11px] font-black uppercase text-white/80 transition hover:bg-white/10 disabled:opacity-40"
            >
              <Boxes size={13} />
              {community3DActionLabel} Community 3D ({communityCompileZones.length}{' '}
              {communityCompileZones.length === 1 ? 'zone' : 'zones'})
            </button>
          ) : (
            <div className="mt-2 rounded border border-amber-400/40 bg-amber-400/10 p-2.5 text-[11px] text-amber-100">
              <p className="font-bold">
                {community3DActionLabel} {communityCompileBuildingCount} building{communityCompileBuildingCount === 1 ? '' : 's'}, {communityCompileParkCount} park{communityCompileParkCount === 1 ? '' : 's'}, and {communityCompileStreetCount} street{communityCompileStreetCount === 1 ? '' : 's'} in 3D?
              </p>
              <p className="mt-1 text-amber-100/70">
                Uses the same atomic compiler as LEGO Builder and no external model-generation credits.
                Supported families use detailed modular GLBs; families still being authored use honest exact-footprint 3D massing.
                Parks and engineered street sections compile in the same transaction. The editable tile scene intentionally leaves out
                trees, benches and loose furniture; Render adds them after paths, water, crossings and fixed programs are known.
                AI park ground drapes remain an optional Gemini step below.
              </p>
              <div className="mt-2 flex gap-2">
                <button
                  type="button"
                  onClick={handleGenerate3D}
                  disabled={isQueuing3D}
                  className="flex-1 rounded border border-[#151515] bg-[#c9ff3d] px-2 py-1.5 font-black uppercase text-[#151515] transition hover:bg-[#d8ff70] disabled:opacity-50"
                >
                  {isQueuing3D ? 'Queueing…' : 'Confirm'}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirm3DOpen(false)}
                  disabled={isQueuing3D}
                  className="flex-1 rounded border border-white/20 bg-white/5 px-2 py-1.5 font-black uppercase text-white/70 transition hover:bg-white/10"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {generate3DStatus && (
            <p className="mt-2 text-[11px] text-emerald-300/90">{generate3DStatus}</p>
          )}

          {parkZones.length > 0 && (
            <>
              {selectedParkNeedingGround && (
                <button
                  type="button"
                  onClick={handleGenerateSelectedParkGround}
                  disabled={planGeometryStale || isGeneratingParks}
                  title="Optional: replace the selected park's complete procedural ground material with one geometry-matched Gemini drape"
                  className="mt-2 flex w-full items-center justify-center gap-2 rounded border border-[#151515] bg-[#c9ff3d] px-3 py-2 text-[11px] font-black uppercase text-[#151515] transition hover:bg-[#d8ff70] disabled:opacity-40"
                >
                  {isGeneratingParks ? <Loader2 size={13} className="animate-spin" /> : <Trees size={13} />}
                  Optional AI Ground Upgrade (1 call)
                </button>
              )}
              {parkHasGroundToRegenerate && (
                <button
                  type="button"
                  onClick={handleRegenerateParkGround}
                  disabled={planGeometryStale || isGeneratingParks}
                  title="Replace this park's AI ground material using the latest geometry-lock prompt (one Gemini call)"
                  className="mt-2 flex w-full items-center justify-center gap-2 rounded border border-amber-300/50 bg-amber-300/10 px-3 py-2 text-[11px] font-black uppercase text-amber-100 transition hover:bg-amber-300/20 disabled:opacity-40"
                >
                  {isGeneratingParks ? <Loader2 size={13} className="animate-spin" /> : <Trees size={13} />}
                  Regenerate AI Ground (1 call)
                </button>
              )}
              <button
              type="button"
              onClick={handleGenerateParkGrounds}
              disabled={planGeometryStale || isGeneratingParks || parksNeedingGround.length === 0}
              title={
                planGeometryStale
                  ? stalePlanMessage ?? 'Redraw the master plan for this boundary'
                  : parksNeedingGround.length === 0
                  ? 'All park zones already have optional AI ground drapes'
                  : `Optional material upgrade: replace the next ${parkGroundBatch.length} of ${parksNeedingGround.length} complete procedural park grounds with geometry-matched Gemini drapes (one call each; ${MAX_PARK_GROUND_BATCH_CALLS}-call safety cap). This is not required for Community 3D or Render; the final render adds realistic planting and furniture.`
              }
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border border-white/20 bg-white/5 px-3 py-2 text-[11px] font-black uppercase text-white/80 transition hover:bg-white/10 disabled:opacity-40"
            >
              {isGeneratingParks ? <Loader2 size={13} className="animate-spin" /> : <Trees size={13} />}
              {isGeneratingParks
                ? 'Generating Optional AI Grounds…'
                : `Optional AI Park Grounds (${parkGroundBatch.length} call${parkGroundBatch.length === 1 ? '' : 's'})`}
              </button>
            </>
          )}
          {parkGroundStatus && (
            <p className="mt-2 text-[11px] text-emerald-300/90">{parkGroundStatus}</p>
          )}
        </div>
      )}

      {/* Saved renders gallery */}
      {projectId && (
        <div className="border-t-2 border-white/10 px-4 py-3">
          <button
            onClick={() => setShowSavedRenders((v) => !v)}
            className="flex w-full items-center justify-between text-xs font-black uppercase text-white/55 transition hover:text-white"
          >
            <span className="flex items-center gap-1.5">
              <ImageIcon size={13} />
              Saved Renders
            </span>
            <span>{savedRenders.length}</span>
          </button>

          {showSavedRenders && (
            <div className="mt-3">
              {savedRenders.length === 0 ? (
                <p className="py-3 text-center text-xs text-gray-500">
                  Save a render to keep it with this project.
                </p>
              ) : (
                <div className="grid grid-cols-3 gap-2">
                  {savedRenders.map((saved) => {
                    const savedUrl = resolveApiFileUrl(saved.image_url);
                    return (
                      <button
                        key={saved.id}
                        onClick={() => openSavedRenderLightbox(saved)}
                        className="group relative aspect-square overflow-hidden rounded border border-white/10 transition hover:border-amber-400/60"
                        title="Open saved render"
                      >
                        <img
                          src={savedUrl}
                          alt={saved.prompt || 'Saved render'}
                          className="h-full w-full object-cover"
                        />
                        <span className="absolute inset-x-0 bottom-0 truncate bg-black/65 px-1 py-0.5 text-left text-[9px] text-white/80 opacity-0 transition group-hover:opacity-100">
                          {saved.style || new Date(saved.created_at).toLocaleDateString()}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      )}
      </div>
      )}

      {/* Render button */}
      <div className="shrink-0 border-t-2 border-[#151515] bg-[#fff9ec] px-4 py-3">
        {stalePlanMessage && (
          <p className="mb-2 rounded border border-red-500/40 bg-red-50 px-2.5 py-2 text-[11px] font-bold text-red-800">
            Redraw the master plan for the current boundary before rendering.
          </p>
        )}
        <button
          onClick={handleRender}
          disabled={planGeometryStale || isRendering || !canvas || !camera}
          className="flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-gradient-to-r from-[#28c7e8] via-[#c9ff3d] to-[#ffe45e] px-4 py-2.5 text-sm font-black text-[#151515] shadow-[5px_5px_0_0_#151515] transition hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
        >
          {isRendering ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              <span className="min-w-0 truncate">
                {isPreparingCapture
                  ? `Preparing Google tiles... ${renderTime > 0 ? `(${renderTime}s)` : ''}`
                  : renderProgress
                  ? `Rendering ${renderProgress.step}/${renderProgress.total}: ${renderProgress.zoneName}... ${renderTime > 0 ? `(${renderTime}s)` : ''}`
                  : `Rendering current view... ${renderTime > 0 ? `(${renderTime}s)` : ''}`
                }
              </span>
            </>
          ) : planGeometryStale ? (
            <>
              <Camera size={16} />
              <span>Plan boundary changed</span>
            </>
          ) : (
            <>
              <Camera size={16} />
              <span className="flex min-w-0 flex-col leading-tight">
                <span>Generate Current View Previews</span>
                <span className="text-[10px] font-bold opacity-70">
                  {renderCallCount} image call{renderCallCount === 1 ? '' : 's'} · uses the globe view on screen now
                </span>
              </span>
            </>
          )}
        </button>
      </div>
    </div>

    {/* Lightbox overlay — click ANYWHERE (including the image), press Esc, or
        click the explicit ✕ button to close. Rendered at the root so it
        overlays the whole viewport regardless of where the panel is mounted. */}
    {lightboxRender && createPortal(
      <div
        className="fixed inset-0 z-[100] flex cursor-zoom-out items-center justify-center bg-black/90 p-6"
        onClick={() => setLightboxRender(null)}
        role="dialog"
        aria-label="Render preview — click anywhere or press Esc to close"
      >
        <div className="absolute right-4 top-4 z-10 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          {lightboxRender.canSave && (
            <button
              onClick={() => saveRenderToProject(lightboxRender)}
              disabled={saving || saveStatus === 'saved'}
              className={`flex h-10 items-center gap-2 rounded-full px-4 text-sm font-semibold shadow-lg ring-2 ring-white/30 transition disabled:cursor-default ${
                saveStatus === 'saved'
                  ? 'bg-green-600 text-white'
                  : saveStatus === 'error'
                    ? 'bg-red-600 text-white hover:bg-red-500'
                    : 'bg-black text-white hover:bg-white hover:text-black'
              }`}
              aria-label="Save render to project"
              title="Save to Project"
            >
              {saving ? <Loader2 size={16} className="animate-spin" /> : saveStatus === 'saved' ? <Check size={16} /> : null}
              {saving ? 'Saving...' : saveStatus === 'saved' ? 'Saved' : saveStatus === 'error' ? 'Retry Save' : 'Save to Project'}
            </button>
          )}
          <a
            href={lightboxRender.imageUrl}
            download={lightboxRender.downloadName}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-black text-white shadow-lg ring-2 ring-white/30 transition hover:bg-white hover:text-black"
            aria-label="Download render"
            title="Download"
          >
            <Download size={20} />
          </a>
          <button
            onClick={() => setLightboxRender(null)}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-black text-white shadow-lg ring-2 ring-white/30 transition hover:bg-white hover:text-black"
            aria-label="Close"
            title="Close (Esc)"
          >
            <X size={22} />
          </button>
        </div>
        <div className="flex max-h-full max-w-full flex-col items-center gap-3" onClick={(e) => e.stopPropagation()}>
          <img
            src={lightboxRender.imageUrl}
            alt="Enlarged render"
            className="max-h-[82vh] max-w-[92vw] rounded-lg object-contain shadow-2xl"
          />
          {(lightboxRender.prompt || getLightboxMetaParts(lightboxRender).length > 0) && (
            <div className="max-w-3xl rounded-lg bg-black/60 px-4 py-2 text-center text-xs text-white/75">
              {lightboxRender.prompt && <p className="line-clamp-2">{lightboxRender.prompt}</p>}
              {getLightboxMetaParts(lightboxRender).length > 0 && (
                <p className="mt-1 text-white/45">
                  {[lightboxRender.providerLabel, lightboxRender.style, lightboxRender.createdAt ? new Date(lightboxRender.createdAt).toLocaleDateString() : null]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              )}
            </div>
          )}
        </div>
      </div>,
      document.body,
    )}
    </>
  );
}
