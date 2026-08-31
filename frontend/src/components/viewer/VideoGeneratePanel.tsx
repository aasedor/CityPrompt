import {
  Check,
  Clapperboard,
  Download,
  Film,
  Loader2,
  MapPinned,
  RefreshCw,
  ShieldCheck,
  Star,
  X,
} from 'lucide-react';
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type MouseEvent as ReactMouseEvent,
} from 'react';
import { createPortal } from 'react-dom';
import toast from 'react-hot-toast';

import { getApiErrorMessage, resolveApiFileUrl, videoRenderApi } from '@/services/api';
import type { Building, SiteZone } from '@/types';
import { getCommunity3DCaptureClaims } from '@/features/community3d/community3d';
import { getCurrentResidualLandscapeClaim } from './globe/residualLandscape';
import {
  appendRoutePoint,
  normalizedRoutePoint,
  routeSignature,
  routeSvgPoints,
  type VideoRoutePoint,
} from './videoRenderPath';
import { buildVideoSceneContract } from './videoSceneContract';
import {
  type VideoControlMode,
  type VideoRouteCaptureRequest,
  type VideoRouteCaptureResult,
} from './videoRouteControls';
import {
  VIDEO_RENDER_QUALITY_PROFILES,
  videoRenderQualityProfile,
  type VideoRenderQuality,
} from './videoRenderQuality';

const MOTIONS = [
  { id: 'path_follow', name: 'Aerial fly-through', detail: 'Slow + high oblique' },
  { id: 'street_walkby', name: 'Street walk-by', detail: 'Slow + pedestrian height' },
  { id: 'detail_flythrough', name: 'Low detail fly-through', detail: '6 m · between buildings' },
] as const;

const CONTROL_MODES: Array<{ id: VideoControlMode; name: string; detail: string }> = [
  { id: 'preview_video', name: 'Preview-video edit', detail: 'Recommended · exact 8-second camera' },
  { id: 'multi_keyframe', name: 'Route keyframes', detail: 'Experimental · 6 exact City Prompt views' },
  { id: 'single_frame', name: 'Single frame', detail: 'Original baseline method' },
];

type MotionId = typeof MOTIONS[number]['id'];
type VideoProvider = 'omni' | 'seedance_mini' | 'internal_enhance';
type SeedanceReferenceMode = 'preview_only' | 'preview_plus_keyframes';
type InternalEnhanceQuality = 'fast' | 'gpu_detail';

const PROVIDERS: Array<{ id: VideoProvider; name: string; detail: string }> = [
  { id: 'omni', name: 'Gemini Omni', detail: 'Video-to-video finish · $0.80 estimate' },
  { id: 'seedance_mini', name: 'Seedance Mini', detail: 'fal pilot · maximum 4 calls' },
  { id: 'internal_enhance', name: 'Internal Enhance', detail: 'Self-hosted · exact skins · $0' },
];

function providerName(provider?: VideoProvider): string {
  if (provider === 'seedance_mini') return 'Seedance Mini';
  if (provider === 'internal_enhance') return 'Internal Enhance';
  return 'Omni';
}

function providerSlug(provider?: VideoProvider): string {
  if (provider === 'seedance_mini') return 'seedance-mini';
  if (provider === 'internal_enhance') return 'internal-enhance';
  return 'omni';
}

function providerOrigin(provider?: VideoProvider): string {
  if (provider === 'seedance_mini') return 'fal Seedance Mini';
  if (provider === 'internal_enhance') return 'City Prompt local pipeline';
  return 'Gemini Omni';
}

function sceneClaimsSignature(
  claims: PreparedVideoRequest['community_3d_claims'] | null,
  residual: PreparedVideoRequest['residual_landscape_claim'] | null,
): string {
  if (!claims || claims.length === 0) return 'scene-not-current';
  return [
    ...claims
      .map((claim) => `${claim.zone_id}:${claim.source_hash}:${claim.representation_hash}:${claim.building_id ?? ''}`)
      .sort(),
    residual
      ? `${residual.boundary_id}:${residual.source_hash}`
      : 'no-site-boundary',
  ].join('|');
}

export interface VideoAttempt {
  id: string;
  request_id: string;
  provider?: VideoProvider;
  model?: string | null;
  seedance_reference_mode?: SeedanceReferenceMode | null;
  internal_enhance_quality?: InternalEnhanceQuality | null;
  render_quality?: VideoRenderQuality | null;
  capture_profile?: VideoCaptureProfile | null;
  status: string;
  style: string;
  control_mode?: VideoControlMode;
  camera_motion: string;
  duration_seconds: number;
  created_at: string;
  video_url?: string | null;
  guide_image_url?: string | null;
  error?: string | null;
  interaction_id?: string | null;
  prompt?: string | null;
  estimated_cost_usd: number;
  fidelity_score?: number | null;
  fidelity_min_score?: number | null;
  fidelity_status?: 'pending' | 'stable' | 'review' | 'drift' | 'unavailable' | null;
  fidelity_samples?: Array<{ time_seconds: number; score: number }>;
  is_benchmark?: boolean;
  benchmark_source?: 'automatic' | 'user' | null;
  enhancement_engine?: string | null;
  resource_count?: number;
  resource_asset_count?: number;
  resource_families?: string[];
  resource_strategy?: string | null;
  processing_seconds?: number | null;
  enhancement_warning?: string | null;
  scene_revision_sha256?: string | null;
}

function fidelityTone(status: VideoAttempt['fidelity_status']): string {
  if (status === 'stable') return 'bg-[#c9ff3d] text-[#151515]';
  if (status === 'review') return 'bg-[#ffd76a] text-[#151515]';
  if (status === 'drift') return 'bg-[#ffb5a9] text-[#8d2c23]';
  return 'bg-[#eee8dc] text-[#151515]/55';
}

function videoAttemptLabel(attempt: VideoAttempt): string {
  const provider = providerName(attempt.provider);
  const motion = attempt.camera_motion.split('_').join(' ');
  const control = attempt.provider === 'seedance_mini'
    ? attempt.seedance_reference_mode === 'preview_plus_keyframes' ? 'Preview + 3 views' : 'Preview only'
    : attempt.provider === 'internal_enhance'
      ? 'Source-locked cleanup'
    : attempt.control_mode === 'multi_keyframe'
      ? 'Route keyframes'
      : attempt.control_mode === 'preview_video'
        ? 'Preview-video edit'
        : 'Single frame';
  if (attempt.style === 'source_fidelity') return `${provider} · ${control} · ${motion}`;
  return `${provider} · ${attempt.style.split(/[_-]/).join(' ')} · ${motion}`;
}

interface ProviderUsage {
  attempts_used: number;
  attempts_remaining: number | null;
  max_attempts: number | null;
}

interface VideoPilotState {
  attempts: VideoAttempt[];
  attempts_used: number;
  attempts_remaining: number;
  max_attempts: number;
  provider_usage: Record<VideoProvider, ProviderUsage>;
}

interface PreflightResult {
  ready: boolean;
  provider_called: false;
  width: number;
  height: number;
  mime_type: string;
  prompt_preview: string;
  provider: VideoProvider;
  attempts_used: number;
  attempts_remaining: number | null;
  max_attempts: number | null;
  estimated_cost_usd: number;
  model: string;
  reference_image_count: number;
  scene_revision_sha256: string;
}

interface VideoCaptureProfile {
  encoder: 'webcodecs_h264' | 'media_recorder_webm';
  fixed_timestep: true;
  frame_count: 192;
  fps: 24;
  width: number;
  height: number;
  render_width: number;
  render_height: number;
  tile_warmup_frame_count: number;
  tile_set_held: boolean;
  geometry_checkpoint_count: number;
  semantic_checkpoint_count: number;
  instance_checkpoint_count: number;
  depth_checkpoint_count: number;
  normal_checkpoint_count: number;
  material_checkpoint_count: number;
  motion_frame_count: number;
}

interface PreparedVideoRequest {
  project_id: string;
  provider: VideoProvider;
  seedance_reference_mode: SeedanceReferenceMode;
  internal_enhance_quality: InternalEnhanceQuality;
  render_quality: VideoRenderQuality;
  guide_frame_base64: string;
  control_mode: VideoControlMode;
  route_keyframes_base64: string[];
  preview_video_base64?: string;
  preview_video_mime_type?: string;
  geometry_checkpoints?: Array<{
    progress: number;
    beauty_image_base64: string;
    object_id_image_base64: string;
    object_id_manifest: Record<string, string>;
    instance_id_image_base64: string;
    instance_id_manifest: Record<string, unknown>;
    depth_image_base64: string;
    normal_image_base64: string;
    material_id_image_base64: string;
    material_id_manifest: Record<string, unknown>;
    camera: NonNullable<VideoRouteCaptureResult['geometryCheckpoints']>[number]['camera'];
  }>;
  capture_profile?: VideoCaptureProfile;
  route_points: VideoRoutePoint[];
  camera_motion: MotionId;
  duration_seconds: 8;
  scene_brief: string;
  community_3d_claims: Array<{
    zone_id: string;
    source_hash: string;
    representation_hash: string;
    building_id?: string;
  }>;
  residual_landscape_claim?: {
    boundary_id: string;
    source_hash: string;
  };
}

interface VideoGeneratePanelProps {
  projectId: string;
  canvas: HTMLCanvasElement | null;
  siteZones: SiteZone[];
  buildings: Building[];
  waitForTilesSettled?: () => Promise<boolean>;
  onBeforeCapture?: () => Promise<void>;
  captureAerialFrame?: () => Promise<string | null>;
  captureRouteControls?: (request: VideoRouteCaptureRequest) => Promise<VideoRouteCaptureResult>;
  onVideoSaved?: (attempt: VideoAttempt) => void;
  onClose: () => void;
}

function loadImage(source: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error('The captured scene could not be prepared.'));
    image.src = source;
  });
}

async function normalizeImageFrame(
  source: string,
  quality: VideoRenderQuality,
): Promise<string> {
  const profile = videoRenderQualityProfile(quality);
  const image = await loadImage(source);
  const output = document.createElement('canvas');
  output.width = profile.outputWidth;
  output.height = profile.outputHeight;
  const context = output.getContext('2d');
  if (!context) throw new Error('This browser cannot prepare a video frame.');

  const sourceAspect = image.naturalWidth / image.naturalHeight;
  const targetAspect = profile.outputWidth / profile.outputHeight;
  let sx = 0;
  let sy = 0;
  let sw = image.naturalWidth;
  let sh = image.naturalHeight;
  if (sourceAspect > targetAspect) {
    sw = image.naturalHeight * targetAspect;
    sx = (image.naturalWidth - sw) / 2;
  } else {
    sh = image.naturalWidth / targetAspect;
    sy = (image.naturalHeight - sh) / 2;
  }
  context.drawImage(image, sx, sy, sw, sh, 0, 0, profile.outputWidth, profile.outputHeight);
  return output.toDataURL('image/jpeg', 0.94);
}

async function captureSceneFrame(
  canvas: HTMLCanvasElement,
  quality: VideoRenderQuality,
): Promise<string> {
  const profile = videoRenderQualityProfile(quality);
  await new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
  const output = document.createElement('canvas');
  output.width = profile.outputWidth;
  output.height = profile.outputHeight;
  const context = output.getContext('2d');
  if (!context) throw new Error('This browser cannot prepare a video frame.');

  const sourceWidth = canvas.width;
  const sourceHeight = canvas.height;
  if (sourceWidth < 640 || sourceHeight < 640) {
    throw new Error('Keep the globe visible at a larger size before opening Video Render.');
  }
  const sourceAspect = sourceWidth / sourceHeight;
  const targetAspect = profile.outputWidth / profile.outputHeight;
  let sx = 0;
  let sy = 0;
  let sw = sourceWidth;
  let sh = sourceHeight;
  if (sourceAspect > targetAspect) {
    sw = sourceHeight * targetAspect;
    sx = (sourceWidth - sw) / 2;
  } else {
    sh = sourceWidth / targetAspect;
    sy = (sourceHeight - sh) / 2;
  }
  context.drawImage(canvas, sx, sy, sw, sh, 0, 0, profile.outputWidth, profile.outputHeight);
  return output.toDataURL('image/jpeg', 0.94);
}

export function VideoGeneratePanel({
  projectId,
  canvas,
  siteZones,
  buildings,
  waitForTilesSettled,
  onBeforeCapture,
  captureAerialFrame,
  captureRouteControls,
  onVideoSaved,
  onClose,
}: VideoGeneratePanelProps) {
  const [sourceFrame, setSourceFrame] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(true);
  const [routePoints, setRoutePoints] = useState<VideoRoutePoint[]>([]);
  const [motion, setMotion] = useState<MotionId>('path_follow');
  const [provider, setProvider] = useState<VideoProvider>('omni');
  const [seedanceReferenceMode, setSeedanceReferenceMode] = useState<SeedanceReferenceMode>('preview_plus_keyframes');
  const [internalEnhanceQuality, setInternalEnhanceQuality] = useState<InternalEnhanceQuality>('fast');
  const [renderQuality, setRenderQuality] = useState<VideoRenderQuality>('high');
  const [controlMode, setControlMode] = useState<VideoControlMode>('preview_video');
  const [routeControls, setRouteControls] = useState<(VideoRouteCaptureResult & { signature: string }) | null>(null);
  const [isPreparingControls, setIsPreparingControls] = useState(false);
  const [pilot, setPilot] = useState<VideoPilotState>({
    attempts: [],
    attempts_used: 0,
    attempts_remaining: 49,
    max_attempts: 49,
    provider_usage: {
      omni: { attempts_used: 0, attempts_remaining: 49, max_attempts: 49 },
      seedance_mini: { attempts_used: 0, attempts_remaining: 4, max_attempts: 4 },
      internal_enhance: { attempts_used: 0, attempts_remaining: null, max_attempts: null },
    },
  });
  const [preflight, setPreflight] = useState<PreflightResult | null>(null);
  const [prepared, setPrepared] = useState<PreparedVideoRequest | null>(null);
  const [isPreflighting, setIsPreflighting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isScoring, setIsScoring] = useState(false);
  const [isBenchmarking, setIsBenchmarking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAttempt, setSelectedAttempt] = useState<VideoAttempt | null>(null);
  const captureStarted = useRef(false);
  const captureSequence = useRef(0);
  const sceneContract = useMemo(() => buildVideoSceneContract(siteZones), [siteZones]);
  const community3DClaims = useMemo(
    () => getCommunity3DCaptureClaims(siteZones, buildings),
    [buildings, siteZones],
  );
  const residualLandscapeClaim = useMemo(
    () => getCurrentResidualLandscapeClaim(siteZones),
    [siteZones],
  );
  const currentSceneRevisionSignature = useMemo(
    () => sceneClaimsSignature(community3DClaims, residualLandscapeClaim),
    [community3DClaims, residualLandscapeClaim],
  );
  const routeCaptureSignature = useMemo(
    () => `${renderQuality}:${motion}:${routeSignature(routePoints)}`,
    [motion, renderQuality, routePoints],
  );

  const currentSignature = useMemo(
    () => `${provider}:${seedanceReferenceMode}:${internalEnhanceQuality}:${renderQuality}:${controlMode}:${motion}:${routeSignature(routePoints)}:${sceneContract.signature}:${currentSceneRevisionSignature}`,
    [controlMode, currentSceneRevisionSignature, internalEnhanceQuality, motion, provider, renderQuality, routePoints, sceneContract.signature, seedanceReferenceMode],
  );
  const preparedSignature = prepared
    ? `${prepared.provider}:${prepared.seedance_reference_mode}:${prepared.internal_enhance_quality}:${prepared.render_quality}:${prepared.control_mode}:${prepared.camera_motion}:${routeSignature(prepared.route_points)}:${prepared.scene_brief.startsWith(sceneContract.text) ? sceneContract.signature : 'stale'}:${sceneClaimsSignature(prepared.community_3d_claims, prepared.residual_landscape_claim)}`
    : null;
  const hasValidPreflight = Boolean(preflight?.ready && preparedSignature === currentSignature);
  const providerUsage = pilot.provider_usage[provider];
  const providerCanRun = providerUsage.attempts_remaining === null
    || providerUsage.attempts_remaining > 0;

  const loadPilot = useCallback(async () => {
    try {
      const state = await videoRenderApi.list(projectId) as VideoPilotState;
      setPilot({
        ...state,
        provider_usage: {
          omni: state.provider_usage?.omni ?? {
            attempts_used: state.attempts_used,
            attempts_remaining: state.attempts_remaining,
            max_attempts: state.max_attempts,
          },
          seedance_mini: state.provider_usage?.seedance_mini
            ?? { attempts_used: 0, attempts_remaining: 4, max_attempts: 4 },
          internal_enhance: state.provider_usage?.internal_enhance
            ?? { attempts_used: 0, attempts_remaining: null, max_attempts: null },
        },
      });
      setSelectedAttempt((current) => (
        (current ? state.attempts.find((attempt) => attempt.id === current.id) : null)
        ?? state.attempts.find((attempt) => attempt.status === 'complete')
        ?? null
      ));
    } catch (loadError) {
      setError(getApiErrorMessage(loadError, 'Could not load Video Render history.'));
    }
  }, [projectId]);

  const capture = useCallback(async (quality = renderQuality) => {
    const sequence = ++captureSequence.current;
    if (!canvas && !captureAerialFrame) {
      if (sequence === captureSequence.current) {
        setError('The 3D globe is still starting. Close Video Render and try again in a moment.');
        setIsCapturing(false);
      }
      return;
    }
    setIsCapturing(true);
    setError(null);
    try {
      await onBeforeCapture?.();
      const settled = await waitForTilesSettled?.();
      if (settled === false) {
        toast('Captured the visible site; distant background tiles are still refining.', { icon: '◌' });
      }
      const directCapture = await captureAerialFrame?.();
      const captured = directCapture
        ? await normalizeImageFrame(
            directCapture.startsWith('data:') ? directCapture : `data:image/png;base64,${directCapture}`,
            quality,
          )
        : await captureSceneFrame(canvas!, quality);
      if (sequence === captureSequence.current) {
        setSourceFrame(captured);
        setRouteControls(null);
        setPreflight(null);
        setPrepared(null);
      }
    } catch (captureError) {
      if (sequence === captureSequence.current) {
        setError(getApiErrorMessage(captureError, 'The current globe view could not be captured.'));
      }
    } finally {
      if (sequence === captureSequence.current) setIsCapturing(false);
    }
  }, [canvas, captureAerialFrame, onBeforeCapture, renderQuality, waitForTilesSettled]);

  const selectMotion = useCallback((nextMotion: MotionId) => {
    setMotion(nextMotion);
    setRouteControls(null);
    setRoutePoints([]);
    setPreflight(null);
    setPrepared(null);
  }, []);

  useEffect(() => {
    void loadPilot();
    if (!captureStarted.current) {
      captureStarted.current = true;
      void capture();
    }
  }, [capture, loadPilot]);

  useEffect(() => {
    if (preparedSignature && preparedSignature !== currentSignature) {
      setPreflight(null);
      setPrepared(null);
    }
  }, [currentSignature, preparedSignature]);

  const requestBody = useCallback(async (): Promise<PreparedVideoRequest> => {
    if (!sourceFrame) throw new Error('Capture the scene before validating.');
    if (routePoints.length < 2) throw new Error('Draw a route with a start and finish.');
    if (!community3DClaims || community3DClaims.length === 0) {
      throw new Error('The compiled scene changed. Close Video Render, run Generate to 3D, and capture it again.');
    }
    let activeControls = routeControls?.signature === routeCaptureSignature ? routeControls : null;
    if (controlMode !== 'single_frame' && !activeControls) {
      if (!captureRouteControls) throw new Error('This 3D view cannot prepare route controls yet.');
      setIsPreparingControls(true);
      try {
        const captured = await captureRouteControls({
          routePoints,
          cameraMotion: motion,
          renderQuality,
          durationSeconds: 8,
          keyframeCount: 6,
        });
        const normalizedKeyframes = await Promise.all(captured.keyframesBase64.map((frame) => (
          normalizeImageFrame(
            frame.startsWith('data:') ? frame : `data:image/png;base64,${frame}`,
            renderQuality,
          )
        )));
        activeControls = {
          ...captured,
          keyframesBase64: normalizedKeyframes,
          signature: routeCaptureSignature,
        };
        setRouteControls(activeControls);
      } finally {
        setIsPreparingControls(false);
      }
    }

    const sceneBrief = provider === 'internal_enhance'
      ? `${sceneContract.text}\nSOURCE POLICY: The deterministic City Prompt route preview already contains the approved render-locked GLB skins, open-space assets, context buildings, and exact camera timing. Restore only detail present in those pixels. Do not synthesize or reinterpret any object.`
      : controlMode === 'multi_keyframe'
      ? `${sceneContract.text}\nSOURCE POLICY: The ordered City Prompt route images are the only visual authorities. They depict one unchanged scene along the exact desired path. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`
      : controlMode === 'preview_video'
        ? `${sceneContract.text}\nSOURCE POLICY: The City Prompt route preview is the exact camera, geography, and geometry authority. Preserve every frame's layout, topology, context, and timing. Omni may improve only the physically plausible visual finish already implied by the source; it must not redesign or relocate anything.`
        : `${sceneContract.text}\nSOURCE POLICY: Image1 is the only visual input. Animate the captured scene as-is. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`;
    const allRouteKeyframes = activeControls?.keyframesBase64 ?? [];
    const routeKeyframes = controlMode === 'multi_keyframe'
      ? allRouteKeyframes
      : provider === 'seedance_mini' && seedanceReferenceMode === 'preview_plus_keyframes' && allRouteKeyframes.length >= 3
        ? [
            allRouteKeyframes[0],
            allRouteKeyframes[Math.floor((allRouteKeyframes.length - 1) / 2)],
            allRouteKeyframes[allRouteKeyframes.length - 1],
          ]
        : [];
    return {
      project_id: projectId,
      provider,
      seedance_reference_mode: seedanceReferenceMode,
      internal_enhance_quality: internalEnhanceQuality,
      render_quality: renderQuality,
      guide_frame_base64: routeKeyframes[0] ?? sourceFrame,
      control_mode: controlMode,
      route_keyframes_base64: routeKeyframes,
      ...(controlMode === 'preview_video' && activeControls ? {
        preview_video_base64: activeControls.previewVideoBase64,
        preview_video_mime_type: activeControls.previewVideoMimeType,
      } : {}),
      ...(activeControls?.geometryCheckpoints?.length ? {
        geometry_checkpoints: activeControls.geometryCheckpoints.map((checkpoint) => ({
          progress: checkpoint.progress,
          beauty_image_base64: checkpoint.beautyImageBase64,
          object_id_image_base64: checkpoint.classIdImageBase64,
          object_id_manifest: { ...checkpoint.classIdManifest },
          instance_id_image_base64: checkpoint.instanceIdImageBase64,
          instance_id_manifest: { ...checkpoint.instanceIdManifest },
          depth_image_base64: checkpoint.depthImageBase64,
          normal_image_base64: checkpoint.normalImageBase64,
          material_id_image_base64: checkpoint.materialIdImageBase64,
          material_id_manifest: { ...checkpoint.materialIdManifest },
          camera: checkpoint.camera,
        })),
      } : {}),
      ...(activeControls?.previewCaptureProfile ? {
        capture_profile: {
          encoder: activeControls.previewCaptureProfile.encoder,
          fixed_timestep: true,
          frame_count: 192,
          fps: 24,
          width: activeControls.previewCaptureProfile.width,
          height: activeControls.previewCaptureProfile.height,
          render_width: activeControls.previewCaptureProfile.renderWidth ?? activeControls.previewCaptureProfile.width,
          render_height: activeControls.previewCaptureProfile.renderHeight ?? activeControls.previewCaptureProfile.height,
          tile_warmup_frame_count: activeControls.previewCaptureProfile.tileWarmupFrameCount ?? 0,
          tile_set_held: activeControls.previewCaptureProfile.tileSetHeld ?? false,
          geometry_checkpoint_count: activeControls.geometryPassProfile?.checkpointCount ?? 0,
          semantic_checkpoint_count: activeControls.geometryPassProfile?.semanticCheckpointCount ?? 0,
          instance_checkpoint_count: activeControls.geometryPassProfile?.instanceCheckpointCount ?? 0,
          depth_checkpoint_count: activeControls.geometryPassProfile?.depthCheckpointCount ?? 0,
          normal_checkpoint_count: activeControls.geometryPassProfile?.normalCheckpointCount ?? 0,
          material_checkpoint_count: activeControls.geometryPassProfile?.materialCheckpointCount ?? 0,
          motion_frame_count: activeControls.geometryPassProfile?.motionFrameCount ?? 0,
        },
      } : {}),
      route_points: routePoints,
      camera_motion: motion,
      duration_seconds: 8,
      scene_brief: sceneBrief,
      community_3d_claims: community3DClaims,
      ...(residualLandscapeClaim ? {
        residual_landscape_claim: residualLandscapeClaim,
      } : {}),
    };
  }, [captureRouteControls, community3DClaims, controlMode, internalEnhanceQuality, motion, projectId, provider, renderQuality, residualLandscapeClaim, routeCaptureSignature, routeControls, routePoints, sceneContract, seedanceReferenceMode, sourceFrame]);

  const runPreflight = useCallback(async () => {
    setIsPreflighting(true);
    setError(null);
    try {
      const body = await requestBody();
      const result = await videoRenderApi.preflight(body) as PreflightResult;
      setPrepared(body);
      setPreflight(result);
      setPilot((current) => ({
        ...current,
        provider_usage: {
          ...current.provider_usage,
          [result.provider]: {
            attempts_used: result.attempts_used,
            attempts_remaining: result.attempts_remaining,
            max_attempts: result.max_attempts,
          },
        },
      }));
      toast.success('Scene and route passed the zero-cost check');
    } catch (preflightError) {
      setPreflight(null);
      setPrepared(null);
      setError(getApiErrorMessage(preflightError, 'Video preflight failed.'));
    } finally {
      setIsPreflighting(false);
    }
  }, [requestBody]);

  const generate = useCallback(async () => {
    if (!prepared || !hasValidPreflight || !providerCanRun) return;
    setIsGenerating(true);
    setError(null);
    try {
      const result = await videoRenderApi.generate({
        ...prepared,
        request_id: crypto.randomUUID(),
        confirm_paid_submission: true,
      }) as { attempt: VideoAttempt; attempts_used: number; attempts_remaining: number | null };
      setSelectedAttempt(result.attempt);
      setPreflight(null);
      setPrepared(null);
      onVideoSaved?.(result.attempt);
      await loadPilot();
      toast.success(`${providerName(prepared.provider)} trial ${result.attempts_used} is ready`);
    } catch (generationError) {
      setError(getApiErrorMessage(generationError, 'The video submission failed.'));
      await loadPilot();
    } finally {
      setIsGenerating(false);
    }
  }, [hasValidPreflight, loadPilot, onVideoSaved, prepared, providerCanRun]);

  const addRouteVertex = (event: ReactMouseEvent<HTMLDivElement>) => {
    if (isGenerating) return;
    setRouteControls(null);
    setPreflight(null);
    setPrepared(null);
    const point = normalizedRoutePoint(event.clientX, event.clientY, event.currentTarget.getBoundingClientRect());
    setRoutePoints((current) => (
      current.length >= 24 ? current : appendRoutePoint(current, point, 0.004)
    ));
  };

  const activeVideoUrl = selectedAttempt?.video_url ? resolveApiFileUrl(selectedAttempt.video_url) : null;
  const unscoredAttempts = pilot.attempts.filter((attempt) => (
    attempt.status === 'complete'
    && attempt.style === 'source_fidelity'
    && typeof attempt.fidelity_score !== 'number'
    && (attempt.control_mode === 'multi_keyframe' || attempt.control_mode === 'preview_video')
  ));
  const scoreSavedVideos = useCallback(async () => {
    setIsScoring(true);
    setError(null);
    try {
      const result = await videoRenderApi.backfillFidelity(projectId) as { attempts_scored: number };
      await loadPilot();
      toast.success(result.attempts_scored > 0
        ? `Scored ${result.attempts_scored} saved video${result.attempts_scored === 1 ? '' : 's'}`
        : 'All eligible videos are already scored');
    } catch (scoreError) {
      setError(getApiErrorMessage(scoreError, 'Saved videos could not be scored.'));
    } finally {
      setIsScoring(false);
    }
  }, [loadPilot, projectId]);
  const setBenchmark = useCallback(async (attempt: VideoAttempt) => {
    if (attempt.provider !== 'omni' || attempt.status !== 'complete') return;
    setIsBenchmarking(true);
    setError(null);
    try {
      await videoRenderApi.setBenchmark(projectId, attempt.id);
      await loadPilot();
      toast.success('Omni benchmark updated');
    } catch (benchmarkError) {
      setError(getApiErrorMessage(benchmarkError, 'The benchmark could not be updated.'));
    } finally {
      setIsBenchmarking(false);
    }
  }, [loadPilot, projectId]);
  const downloadUrl = useCallback((attempt: VideoAttempt) => {
    if (!attempt.video_url) return null;
    const fileName = `city-prompt-${providerSlug(attempt.provider)}-${attempt.style}-${attempt.camera_motion}-${attempt.id.slice(0, 8)}.mp4`;
    const separator = attempt.video_url.includes('?') ? '&' : '?';
    return `${resolveApiFileUrl(attempt.video_url)}${separator}download=true&filename=${encodeURIComponent(fileName)}`;
  }, []);
  const usedDots = providerUsage.max_attempts === null
    ? []
    : Array.from({ length: providerUsage.max_attempts }, (_, index) => index < providerUsage.attempts_used);

  return createPortal(
    <div className="fixed inset-0 z-[240] flex items-center justify-center bg-[#081011]/88 p-3 backdrop-blur-md sm:p-6">
      <div className="flex max-h-[calc(100dvh-1.5rem)] w-full max-w-[1180px] flex-col overflow-hidden rounded-[28px] border-2 border-[#151515] bg-[#f7f2e8] shadow-[10px_10px_0_0_#151515] sm:max-h-[calc(100dvh-3rem)]">
        <header className="flex items-center gap-3 border-b-2 border-[#151515] bg-[#151515] px-4 py-3 text-white sm:px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#28c7e8] to-[#c9ff3d] text-[#151515]">
            <Clapperboard size={18} strokeWidth={2.5} />
          </div>
          <div className="min-w-0">
            <h2 className="text-sm font-black uppercase tracking-[0.14em] sm:text-base">Video Render</h2>
            <p className="truncate text-[11px] text-white/55">Draw the path. Animate the captured scene. Preserve every building.</p>
          </div>
          <div className="ml-auto hidden items-center gap-2 rounded-full border border-white/15 bg-white/[0.06] px-3 py-1.5 sm:flex">
            <span className="text-[10px] font-bold uppercase tracking-wider text-white/50">{provider === 'internal_enhance' ? 'Local runs' : provider === 'seedance_mini' ? 'Seedance calls' : 'Omni calls'}</span>
            <div className="flex gap-1">
              {usedDots.map((used, index) => (
                <span key={index} className={`h-2 w-2 rounded-full ${used ? 'bg-[#ff6b57]' : 'bg-white/20'}`} />
              ))}
            </div>
            <span className="text-xs font-black">
              {providerUsage.max_attempts === null
                ? `${providerUsage.attempts_used} · Unlimited`
                : `${providerUsage.attempts_used}/${providerUsage.max_attempts}`}
            </span>
          </div>
          <button onClick={onClose} disabled={isGenerating} className="rounded-full p-2 text-white/60 transition hover:bg-white/10 hover:text-white disabled:opacity-30" aria-label="Close Video Render">
            <X size={19} />
          </button>
        </header>

        <div className="grid min-h-0 flex-1 overflow-y-auto lg:grid-cols-[minmax(0,1.65fr)_minmax(330px,0.75fr)] lg:overflow-hidden">
          <section className="flex min-h-[430px] flex-col border-b-2 border-[#151515] bg-[#0d1718] p-3 lg:border-b-0 lg:border-r-2 lg:p-5">
            <div className="mb-3 flex flex-wrap items-center gap-2 text-white">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-[10px] font-black uppercase tracking-wider">
                <MapPinned size={12} /> Flight path
              </span>
              <span className="text-[11px] text-white/45">
                {motion === 'street_walkby'
                  ? 'Click ground to add each vertex · the camera faces the site'
                  : motion === 'detail_flythrough'
                    ? 'Click ground between buildings · each click adds a low-flight vertex'
                    : 'Click to add each flight-path vertex · 2 points minimum'}
              </span>
              <span className="rounded-full bg-white/10 px-2 py-1 text-[9px] font-black uppercase text-white/55">
                {routePoints.length} {routePoints.length === 1 ? 'vertex' : 'vertices'}
              </span>
              <button onClick={() => {
                setRouteControls(null);
                setRoutePoints([]);
                setPreflight(null);
                setPrepared(null);
              }} disabled={isGenerating || isPreparingControls} className="ml-auto inline-flex items-center gap-1 rounded-full border border-white/15 px-2.5 py-1 text-[10px] font-bold text-white/65 hover:bg-white/10">
                <RefreshCw size={11} /> Reset route
              </button>
            </div>

            <div className="relative aspect-video w-full overflow-hidden rounded-2xl border border-white/15 bg-black shadow-2xl">
              {sourceFrame && <img src={sourceFrame} alt="Captured City Prompt scene" className="absolute inset-0 h-full w-full select-none object-cover" draggable={false} />}
              {isCapturing && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#111c1d] text-sm font-semibold text-white/65">
                  <Loader2 className="mr-2 animate-spin" size={18} /> Capturing clean 16:9 scene…
                </div>
              )}
              {isPreparingControls && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-[#111c1d]/90 px-8 text-center text-sm font-semibold text-white/75">
                  <Loader2 className="mb-3 animate-spin" size={24} />
                  {renderQuality === 'high'
                    ? 'Dry-traversing all 192 camera poses, freezing Google context, then rendering at 1440p…'
                    : 'Preloading six geographic route views, then rendering 192 fixed camera frames…'}
                  <span className="mt-1 text-[10px] font-normal text-white/45">{renderQuality === 'high' ? 'This can take a few minutes on a laptop.' : 'This may take several seconds.'} No provider call or credit is used.</span>
                </div>
              )}
              {!isCapturing && !sourceFrame && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 px-8 text-center text-sm text-white/60">
                  <Film size={28} />
                  <span>The scene could not be captured.</span>
                  <button onClick={() => void capture()} className="rounded-full bg-white px-4 py-2 text-xs font-black uppercase text-[#151515]">Try capture again</button>
                </div>
              )}
              {sourceFrame && (
                <div
                  className="absolute inset-0 cursor-crosshair touch-none"
                  onClick={addRouteVertex}
                  aria-label={motion === 'street_walkby' ? 'Add pedestrian path vertex' : 'Add drone path vertex'}
                >
                  <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="pointer-events-none absolute inset-0 h-full w-full drop-shadow-[0_2px_2px_rgba(0,0,0,0.9)]">
                    <defs>
                      <marker id="video-route-arrow" markerWidth="5" markerHeight="5" refX="3.5" refY="2.5" orient="auto" markerUnits="strokeWidth">
                        <path d="M0,0 L5,2.5 L0,5 z" fill="#ff3b4f" />
                      </marker>
                    </defs>
                    {routePoints.length > 1 && (
                      <>
                        <polyline points={routeSvgPoints(routePoints)} fill="none" stroke="white" strokeOpacity="0.9" strokeWidth="1.8" vectorEffect="non-scaling-stroke" strokeLinecap="round" strokeLinejoin="round" />
                        <polyline points={routeSvgPoints(routePoints)} fill="none" stroke="#ff3b4f" strokeWidth="1" vectorEffect="non-scaling-stroke" strokeLinecap="round" strokeLinejoin="round" markerEnd="url(#video-route-arrow)" />
                      </>
                    )}
                    {routePoints.map((point, index) => (
                      <g key={`${point.x}-${point.y}-${index}`}>
                        <circle cx={point.x * 100} cy={point.y * 100} r={index === 0 ? 1.6 : 1.1} fill={index === 0 ? 'white' : '#ff3b4f'} stroke="#ff3b4f" strokeWidth="0.7" vectorEffect="non-scaling-stroke" />
                        <text x={point.x * 100} y={point.y * 100} dy="0.35em" textAnchor="middle" fill={index === 0 ? '#151515' : 'white'} fontSize="1.8" fontWeight="900">{index + 1}</text>
                      </g>
                    ))}
                  </svg>
                </div>
              )}
              <div className="pointer-events-none absolute bottom-3 left-3 rounded-full bg-black/65 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-white/75 backdrop-blur">
                16:9 · {videoRenderQualityProfile(renderQuality).outputHeight}p · 8 sec · 192 fixed frames
              </div>
              {motion === 'street_walkby' && (
                <div className="pointer-events-none absolute right-3 top-3 rounded-full border border-[#c9ff3d]/50 bg-[#0d1718]/85 px-3 py-1.5 text-[9px] font-black uppercase tracking-wider text-[#c9ff3d] backdrop-blur">
                  City Prompt authored renderer
                </div>
              )}
            </div>

            {routeControls?.signature === routeCaptureSignature && controlMode !== 'single_frame' && (
              <div className="mt-3 rounded-xl border border-white/10 bg-black/25 p-2">
                <div className="mb-2 flex items-center justify-between text-[9px] font-black uppercase tracking-wider text-white/45">
                  <span>{controlMode === 'multi_keyframe' ? 'Ordered route checkpoints' : 'Deterministic camera preview'}</span>
                  <span className="text-[#c9ff3d]">
                    {routeControls.previewCaptureProfile
                      ? `${routeControls.previewCaptureProfile.frameCount} frames · ${routeControls.previewCaptureProfile.height}p · ${routeControls.previewCaptureProfile.encoder === 'webcodecs_h264' ? 'H.264' : 'WebM fallback'}`
                      : 'Prepared locally'}
                  </span>
                </div>
                {controlMode === 'multi_keyframe' ? (
                  <div className="grid grid-cols-6 gap-1">
                    {routeControls.keyframesBase64.map((frame, index) => (
                      <div key={index} className="relative overflow-hidden rounded border border-white/15 bg-black">
                        <img src={frame} alt={`Route checkpoint ${index + 1}`} className="aspect-video h-full w-full object-cover" />
                        <span className="absolute bottom-0.5 left-0.5 rounded bg-black/70 px-1 text-[8px] font-bold text-white">{index + 1}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <video controls muted playsInline className="aspect-video max-h-36 w-full rounded-lg bg-black object-contain" src={routeControls.previewVideoBase64} />
                )}
                {motion === 'street_walkby' && routeControls.streetRenderReadiness && (
                  <div className="mt-2 rounded-lg border border-white/10 bg-white/[0.05] px-2.5 py-2 text-[9px] text-white/55">
                    <div className="flex flex-wrap items-center gap-x-2 gap-y-1 font-bold">
                      <span className="inline-flex items-center gap-1 uppercase text-[#c9ff3d]"><ShieldCheck size={10} /> Authored scene audit</span>
                      <span>{routeControls.streetRenderReadiness.buildingMeshCount} building meshes</span>
                      <span>{routeControls.streetRenderReadiness.uniquePbrMaterialCount} PBR materials</span>
                      <span>{routeControls.streetRenderReadiness.instancedDetailMeshCount} instanced detail meshes</span>
                      <span>{routeControls.streetRenderReadiness.shadowCasterCount} shadow casters</span>
                      {routeControls.streetRenderReadiness.maxBuildingTextureDimension && (
                        <span>up to {routeControls.streetRenderReadiness.maxBuildingTextureDimension}px textures</span>
                      )}
                    </div>
                    {routeControls.streetRenderReadiness.warnings.length > 0 && (
                      <p className="mt-1 font-semibold text-[#ffd38a]">
                        {routeControls.streetRenderReadiness.warnings.join(' ')}
                      </p>
                    )}
                  </div>
                )}
                {routeControls.previewCaptureProfile?.renderHeight && (
                  <div className="mt-2 flex flex-wrap gap-x-2 gap-y-1 rounded-lg border border-[#c9ff3d]/20 bg-[#c9ff3d]/[0.06] px-2.5 py-2 text-[9px] font-bold text-white/55">
                    <span className="uppercase text-[#c9ff3d]">High-quality source</span>
                    <span>{routeControls.previewCaptureProfile.renderWidth}×{routeControls.previewCaptureProfile.renderHeight} render</span>
                    <span>→ {routeControls.previewCaptureProfile.width}×{routeControls.previewCaptureProfile.height}</span>
                    <span>{routeControls.previewCaptureProfile.tileWarmupFrameCount ?? 0} tile-preload poses</span>
                    {routeControls.geometryPassProfile && (
                      <span>{routeControls.geometryPassProfile.depthCheckpointCount}/{routeControls.geometryPassProfile.checkpointCount} depth + normal checkpoints</span>
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="mt-4 grid min-h-0 gap-3 sm:grid-cols-[1.15fr_0.85fr]">
              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-white/45">Motion control</p>
                <div className="grid grid-cols-3 gap-1.5">
                  {CONTROL_MODES.map((item) => (
                    <button key={item.id} aria-pressed={controlMode === item.id} onClick={() => {
                      if (provider !== 'omni' && item.id !== 'preview_video') return;
                      setControlMode(item.id);
                      setPreflight(null);
                      setPrepared(null);
                    }} disabled={isGenerating || isCapturing || isPreparingControls || (provider !== 'omni' && item.id !== 'preview_video')} className={`rounded-xl border px-2 py-2 text-left transition disabled:cursor-not-allowed disabled:opacity-30 ${controlMode === item.id ? 'border-[#c9ff3d] bg-[#c9ff3d]/15 text-white' : 'border-white/10 bg-white/[0.04] text-white/55 hover:bg-white/[0.08]'}`}>
                      <span className="block text-[10px] font-bold">{item.name}</span>
                      <span className="mt-0.5 block text-[8px] leading-tight opacity-55">{item.detail}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-white/45">Camera behavior</p>
                <div className="grid grid-cols-2 gap-1.5">
                  {MOTIONS.map((item) => (
                    <button key={item.id} aria-pressed={motion === item.id} onClick={() => selectMotion(item.id)} disabled={isGenerating || isCapturing || isPreparingControls} className={`rounded-xl border px-2.5 py-2 text-left transition ${motion === item.id ? 'border-[#28c7e8] bg-[#28c7e8]/15 text-white' : 'border-white/10 bg-white/[0.04] text-white/55 hover:bg-white/[0.08]'}`}>
                      <span className="block text-[11px] font-bold">{item.name}</span>
                      <span className="block text-[9px] opacity-55">{item.detail}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <aside className="flex min-h-0 flex-col bg-[#f7f2e8] lg:overflow-y-auto">
            <div className="space-y-4 p-4 sm:p-5">
              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Source render quality</p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.values(VIDEO_RENDER_QUALITY_PROFILES).map((item) => (
                    <button key={item.id} type="button" aria-pressed={renderQuality === item.id} onClick={() => {
                      setRenderQuality(item.id);
                      setRouteControls(null);
                      setPreflight(null);
                      setPrepared(null);
                      setError(null);
                      void capture(item.id);
                    }} disabled={isGenerating || isPreflighting || isPreparingControls || isCapturing} className={`rounded-xl border-2 p-2.5 text-left transition disabled:opacity-40 ${renderQuality === item.id ? 'border-[#151515] bg-[#fff0bf] shadow-[2px_2px_0_0_#151515]' : 'border-[#151515]/15 bg-white/45 hover:bg-white'}`}>
                      <span className="block text-[10px] font-black">{item.label}</span>
                      <span className="mt-0.5 block text-[8px] leading-tight text-[#151515]/50">{item.detail}</span>
                    </button>
                  ))}
                </div>
                <p className="mt-1.5 text-[8px] font-semibold leading-relaxed text-[#151515]/45">
                  High Quality performs a complete dry traversal, holds Google context tiles, renders at 1440p, and downsamples to 1080p before any local or API animation step.
                </p>
              </div>

              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Video provider</p>
                <div className="grid grid-cols-3 gap-2">
                  {PROVIDERS.map((item) => (
                    <button key={item.id} type="button" aria-pressed={provider === item.id} onClick={() => {
                      setProvider(item.id);
                      if (item.id !== 'omni') setControlMode('preview_video');
                      setPreflight(null);
                      setPrepared(null);
                      setError(null);
                    }} disabled={isGenerating || isPreflighting} className={`rounded-xl border-2 p-2.5 text-left transition disabled:opacity-40 ${provider === item.id ? 'border-[#151515] bg-white shadow-[2px_2px_0_0_#151515]' : 'border-[#151515]/15 bg-white/45 hover:bg-white'}`}>
                      <span className="block text-[10px] font-black">{item.name}</span>
                      <span className="mt-0.5 block text-[8px] leading-tight text-[#151515]/50">{item.detail}</span>
                    </button>
                  ))}
                </div>
                {provider === 'seedance_mini' && (
                  <div className="mt-2 rounded-xl border border-[#151515]/15 bg-[#eef8ff] p-2.5">
                    <p className="mb-1.5 text-[9px] font-black uppercase tracking-wider text-[#151515]/50">Reference package</p>
                    <div className="grid grid-cols-2 gap-1.5">
                      {([
                        { id: 'preview_plus_keyframes' as const, label: 'Preview + 3 views', detail: 'Recommended' },
                        { id: 'preview_only' as const, label: 'Preview only', detail: 'Baseline' },
                      ]).map((item) => (
                        <button key={item.id} type="button" aria-pressed={seedanceReferenceMode === item.id} onClick={() => {
                          setSeedanceReferenceMode(item.id);
                          setPreflight(null);
                          setPrepared(null);
                        }} disabled={isGenerating || isPreflighting} className={`rounded-lg border px-2 py-1.5 text-left ${seedanceReferenceMode === item.id ? 'border-[#28c7e8] bg-white' : 'border-[#151515]/10 bg-white/40'}`}>
                          <span className="block text-[9px] font-black">{item.label}</span>
                          <span className="block text-[8px] text-[#151515]/45">{item.detail}</span>
                        </button>
                      ))}
                    </div>
                    <p className="mt-2 text-[8px] font-semibold leading-relaxed text-[#315d73]">Hard server cap: {providerUsage.attempts_used}/{providerUsage.max_attempts} Seedance submissions. No automatic generation retries.</p>
                  </div>
                )}
                {provider === 'internal_enhance' && (
                  <div className="mt-2 rounded-xl border border-[#151515]/15 bg-[#edf8e7] p-2.5">
                    <p className="text-[9px] font-black uppercase tracking-wider text-[#285b22]">Source-locked local cleanup</p>
                    <p className="mt-1 text-[9px] font-semibold leading-relaxed text-[#315d3a]">Uses the exact route-preview pixels containing City Prompt’s render-locked GLB skins and park assets. No paid API, no scene generation, and no automatic retries.</p>
                    <div className="mt-2 grid grid-cols-2 gap-1.5">
                      {([
                        { id: 'fast' as const, label: 'Fast Cleanup', detail: 'Recommended · seconds' },
                        { id: 'gpu_detail' as const, label: 'GPU Detail', detail: 'Queued · 15–25 min' },
                      ]).map((item) => (
                        <button key={item.id} type="button" aria-pressed={internalEnhanceQuality === item.id} onClick={() => {
                          setInternalEnhanceQuality(item.id);
                          setPreflight(null);
                          setPrepared(null);
                        }} disabled={isGenerating || isPreflighting} className={`rounded-lg border px-2 py-1.5 text-left ${internalEnhanceQuality === item.id ? 'border-[#285b22] bg-white' : 'border-[#151515]/10 bg-white/40'}`}>
                          <span className="block text-[9px] font-black">{item.label}</span>
                          <span className="block text-[8px] text-[#151515]/45">{item.detail}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Scene lock</p>
                  <span className="inline-flex items-center gap-1 rounded-full bg-[#fff0bf] px-2 py-1 text-[9px] font-black uppercase text-[#705000]"><ShieldCheck size={11} /> Continuity constrained</span>
                </div>
                <div className="rounded-xl border border-[#151515]/15 bg-white/65 p-3">
                  <p className="text-xs font-black leading-relaxed text-[#151515]/80">{sceneContract.summary}</p>
                  <p className="mt-1 text-[10px] font-semibold leading-relaxed text-[#151515]/55">
                    The captured pixels lock authored massing, roofs, courtyards, facade rhythm, materials, lighting, Google context buildings, and open-space program. City Prompt adds no moving traffic or pedestrians; any baked Google context remains part of the captured surroundings.
                  </p>
                  <p className="mt-1 text-[10px] font-bold leading-relaxed text-[#151515]/55">
                    {provider === 'internal_enhance'
                      ? motion === 'street_walkby'
                        ? 'Internal Enhance processes the deterministic route locally. Original GLBs, PBR skins, open-space assets, vegetation, and lighting remain authoritative inside the proposal; captured Google Tiles remain the surrounding context.'
                        : 'Internal Enhance processes the deterministic route video locally. Its captured render-locked building skins, open-space assets, Google context, geometry, and timing remain authoritative.'
                      : provider === 'seedance_mini'
                      ? seedanceReferenceMode === 'preview_plus_keyframes'
                        ? 'Seedance receives the exact City Prompt route preview plus three chronological geometry checkpoints.'
                        : 'Seedance receives the exact City Prompt route preview as its sole visual authority.'
                      : controlMode === 'multi_keyframe'
                      ? 'Omni receives six ordered City Prompt views of the same scene, with no style or archetype reference images.'
                      : controlMode === 'preview_video'
                        ? 'Omni edits City Prompt’s deterministic route video, which carries the exact camera timing and scene geometry.'
                        : 'Omni receives one authoritative image plus conservative camera-motion instructions.'}
                  </p>
                  <p className="mt-2 rounded-lg bg-[#fff0bf] px-2 py-1.5 text-[9px] font-bold leading-relaxed text-[#705000]">
                    {provider === 'internal_enhance'
                      ? 'No scene generation: this pass only denoises, sharpens, stabilizes tone, and optionally super-resolves detail already present. The fidelity gate still checks every saved result.'
                      : `AI concept visualization: ${providerName(provider)} can still reinterpret geometry between frames. Verify the video against the 3D scene before using it for design decisions.`}
                  </p>
                </div>
              </div>

              <div className="rounded-2xl border-2 border-[#151515] bg-white p-3 shadow-[3px_3px_0_0_#151515]">
                <div className="flex items-start gap-2">
                  <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${hasValidPreflight ? 'bg-[#c9ff3d]' : 'bg-[#eee8dc]'}`}>
                    {hasValidPreflight ? <Check size={14} strokeWidth={3} /> : <span className="text-[10px] font-black">1</span>}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-black uppercase">Zero-cost preflight</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-[#151515]/50">Prepares route controls, then checks every input, quota, auth, and final prompt. No provider is called.</p>
                  </div>
                </div>
                <button onClick={() => void runPreflight()} disabled={isCapturing || isPreparingControls || isPreflighting || isGenerating || !sourceFrame || routePoints.length < 2 || !providerCanRun} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-[#f7f2e8] px-3 py-2 text-xs font-black uppercase transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40">
                  {isPreflighting ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
                  {isPreflighting ? 'Checking…' : hasValidPreflight ? 'Run check again' : 'Run free check'}
                </button>
                {hasValidPreflight && preflight && (
                  <div className="mt-2 flex items-center gap-2 rounded-lg bg-[#edf8e7] px-2.5 py-2 text-[10px] font-bold text-[#285b22]">
                    <Check size={12} /> Ready · {preflight.width}×{preflight.height} · {controlMode === 'multi_keyframe' ? `${preflight.reference_image_count} route images` : controlMode === 'preview_video' ? 'route-video edit' : 'single frame'} · {preflight.model}
                  </div>
                )}
              </div>

              <div className="rounded-2xl border-2 border-[#151515] bg-[#151515] p-3 text-white shadow-[3px_3px_0_0_#ff6b57]">
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/10 text-[10px] font-black">2</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-black uppercase">{provider === 'internal_enhance' ? `Run ${internalEnhanceQuality === 'gpu_detail' ? 'GPU Detail' : 'Fast Cleanup'}` : `Generate with ${providerName(provider)}`}</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-white/50">{provider === 'internal_enhance' ? `One click = one self-hosted ${internalEnhanceQuality === 'gpu_detail' ? 'model-backed' : 'deterministic'} restoration run at $0.` : 'One click = one paid provider call. There are no automatic retries.'}</p>
                  </div>
                </div>
                <button onClick={() => void generate()} disabled={!hasValidPreflight || isGenerating || !providerCanRun} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border-2 border-white bg-gradient-to-r from-[#28c7e8] to-[#c9ff3d] px-3 py-2.5 text-xs font-black uppercase text-[#151515] transition hover:brightness-105 disabled:cursor-not-allowed disabled:grayscale disabled:opacity-40">
                  {isGenerating ? <Loader2 size={15} className="animate-spin" /> : <Film size={15} />}
                  {isGenerating
                    ? provider === 'internal_enhance' ? 'Restoring exact City Prompt frames…' : 'Rendering one continuous shot…'
                    : provider === 'internal_enhance'
                      ? `${internalEnhanceQuality === 'gpu_detail' ? 'Run GPU pass' : 'Run fast pass'} · unlimited local runs · est. $0.00`
                      : providerCanRun
                        ? `Generate trial ${providerUsage.attempts_used + 1} of ${providerUsage.max_attempts} · est. $${(preflight?.estimated_cost_usd ?? (provider === 'seedance_mini' ? 1.98 : 0.8)).toFixed(2)}`
                        : `${providerUsage.max_attempts}-trial cap reached`}
                </button>
                {isGenerating && <p className="mt-2 text-center text-[10px] text-white/45">{provider === 'internal_enhance' ? 'Keep this panel open while the local frame restoration finishes.' : 'Keep this panel open. High-quality video can take several minutes.'}</p>}
              </div>

              {error && <div role="alert" className="rounded-xl border border-[#c94739]/30 bg-[#ffe5df] px-3 py-2.5 text-[11px] font-semibold leading-relaxed text-[#8d2c23]">{error}</div>}

              {activeVideoUrl && selectedAttempt && (
                <div className="overflow-hidden rounded-2xl border-2 border-[#151515] bg-black shadow-[3px_3px_0_0_#151515]">
                  <video key={activeVideoUrl} controls playsInline autoPlay muted loop className="aspect-video w-full bg-black" src={activeVideoUrl} />
                  <div className="flex items-center gap-2 bg-white px-3 py-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-1.5">
                        <p className="truncate text-[11px] font-black uppercase">{videoAttemptLabel(selectedAttempt)}</p>
                        {selectedAttempt.is_benchmark && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-[#151515] px-2 py-0.5 text-[8px] font-black uppercase text-white">
                            <Star size={9} fill="currentColor" /> Benchmark
                          </span>
                        )}
                        {typeof selectedAttempt.fidelity_score === 'number' && (
                          <span className={`rounded-full px-2 py-0.5 text-[8px] font-black uppercase ${fidelityTone(selectedAttempt.fidelity_status)}`}>
                            Fidelity {Math.round(selectedAttempt.fidelity_score)}/100 · {selectedAttempt.fidelity_status}
                          </span>
                        )}
                      </div>
                      <p className="text-[9px] text-[#151515]/45">
                        8 sec · {selectedAttempt.render_quality === 'high' ? '1080p HQ source' : '720p source'} · {providerOrigin(selectedAttempt.provider)} · saved to project
                        {selectedAttempt.scene_revision_sha256
                          ? ` · scene ${selectedAttempt.scene_revision_sha256.slice(0, 10)}`
                          : ''}
                      </p>
                    </div>
                    {selectedAttempt.provider === 'omni' && !selectedAttempt.is_benchmark && (
                      <button type="button" onClick={() => void setBenchmark(selectedAttempt)} disabled={isBenchmarking} className="inline-flex items-center gap-1 rounded-full border-2 border-[#151515] px-2.5 py-2 text-[9px] font-black uppercase hover:bg-[#f7f2e8] disabled:opacity-40" aria-label="Set as Omni benchmark" title="Set as Omni benchmark">
                        {isBenchmarking ? <Loader2 size={13} className="animate-spin" /> : <Star size={13} />} Benchmark
                      </button>
                    )}
                    <a href={downloadUrl(selectedAttempt) ?? activeVideoUrl} download className="inline-flex items-center gap-1.5 rounded-full border-2 border-[#151515] px-3 py-2 text-[10px] font-black uppercase hover:bg-[#f7f2e8]" aria-label="Download video"><Download size={14} /> MP4</a>
                  </div>
                  {selectedAttempt.provider === 'internal_enhance' && (
                    <div className="border-t border-[#151515]/10 bg-[#edf8e7] px-3 py-2 text-[9px] font-semibold text-[#315d3a]">
                      <span className="font-black uppercase">Exact-resource pass</span>
                      {' · '}{selectedAttempt.resource_count ?? 0} authored families
                      {typeof selectedAttempt.resource_asset_count === 'number' ? ` · ${selectedAttempt.resource_asset_count} render-locked assets` : ''}
                      {selectedAttempt.internal_enhance_quality ? ` · ${selectedAttempt.internal_enhance_quality === 'gpu_detail' ? 'GPU Detail' : 'Fast Cleanup'}` : ''}
                      {selectedAttempt.enhancement_engine ? ` · ${selectedAttempt.enhancement_engine.split('_').join(' ')}` : ''}
                      {typeof selectedAttempt.processing_seconds === 'number' ? ` · ${selectedAttempt.processing_seconds.toFixed(1)}s processing` : ''}
                    </div>
                  )}
                  {selectedAttempt.provider === 'internal_enhance' && selectedAttempt.enhancement_warning && (
                    <div className="border-t border-[#705000]/15 bg-[#fff0bf] px-3 py-2 text-[9px] font-semibold text-[#705000]">
                      GPU Detail did not finish within its guardrail; City Prompt saved the fast source-locked cleanup instead.
                    </div>
                  )}
                  {selectedAttempt.fidelity_samples && selectedAttempt.fidelity_samples.length > 0 && (
                    <div className="flex items-center gap-1.5 border-t border-[#151515]/10 bg-white px-3 py-2" aria-label="Fidelity samples">
                      <span className="mr-1 text-[8px] font-black uppercase text-[#151515]/45">Scene lock</span>
                      {selectedAttempt.fidelity_samples.map((sample) => (
                        <span key={sample.time_seconds} className={`rounded-full px-1.5 py-0.5 text-[8px] font-black ${fidelityTone(sample.score >= 72 ? 'stable' : sample.score >= 52 ? 'review' : 'drift')}`} title={`${sample.time_seconds.toFixed(0)} seconds: ${sample.score.toFixed(1)}/100`}>
                          {sample.time_seconds.toFixed(0)}s {Math.round(sample.score)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {pilot.attempts.length > 0 && (
                <div>
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <p className="text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Pilot history</p>
                    {unscoredAttempts.length > 0 && (
                      <button type="button" onClick={() => void scoreSavedVideos()} disabled={isScoring} className="inline-flex items-center gap-1 rounded-full border border-[#151515]/20 bg-white/60 px-2 py-1 text-[8px] font-black uppercase hover:bg-white disabled:opacity-40">
                        {isScoring ? <Loader2 size={10} className="animate-spin" /> : <ShieldCheck size={10} />}
                        Score saved ({unscoredAttempts.length})
                      </button>
                    )}
                  </div>
                  <div className="space-y-1.5">
                    {pilot.attempts.map((attempt, index) => (
                      <div key={attempt.id} className={`flex w-full items-center gap-1 rounded-xl border px-1.5 py-1 ${selectedAttempt?.id === attempt.id ? 'border-[#151515] bg-white' : 'border-[#151515]/10 bg-white/45'}`}>
                        <button onClick={() => attempt.video_url && setSelectedAttempt(attempt)} className={`flex min-w-0 flex-1 items-center gap-2 rounded-lg px-1 py-1 text-left ${attempt.video_url ? 'hover:bg-[#f7f2e8]' : 'cursor-default'}`}>
                          <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-black ${attempt.status === 'complete' ? 'bg-[#c9ff3d]' : attempt.status === 'failed' ? 'bg-[#ffb5a9]' : 'bg-[#eee8dc]'}`}>{pilot.attempts.length - index}</span>
                          <span className="min-w-0 flex-1 truncate text-[10px] font-bold capitalize">{videoAttemptLabel(attempt)}</span>
                          {attempt.is_benchmark && <Star size={11} fill="currentColor" aria-label="Benchmark" />}
                          {typeof attempt.fidelity_score === 'number' ? (
                            <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-black ${fidelityTone(attempt.fidelity_status)}`} title={`Fidelity ${attempt.fidelity_score.toFixed(1)} of 100`}>
                              {Math.round(attempt.fidelity_score)}
                            </span>
                          ) : (
                            <span className="text-[9px] font-black uppercase text-[#151515]/40">{attempt.status}</span>
                          )}
                        </button>
                        {attempt.video_url && (
                          <a href={downloadUrl(attempt) ?? undefined} download className="rounded-full p-2 hover:bg-[#f7f2e8]" aria-label={`Download ${videoAttemptLabel(attempt)} video`} title="Download MP4">
                            <Download size={13} />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </aside>
        </div>
      </div>
    </div>,
    document.body,
  );
}
