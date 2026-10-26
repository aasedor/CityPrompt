import { isCatalogueOnlyScene, CATALOGUE_UPDATE_GUIDANCE } from '@/features/pickPlace/catalogue';
import { withPeopleDirection } from '@/features/people/peopleActions';
import {
  Check,
  Clapperboard,
  Download,
  Film,
  Loader2,
  MapPinned,
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
} from 'react';
import { createPortal } from 'react-dom';
import toast from 'react-hot-toast';

import { authApi, direct3DAttempts, getApiErrorMessage, resolveApiFileUrl, videoRenderApi } from '@/services/api';
import { assertNearFieldVideoSourceQuality } from './videoSourceQuality';
import { PhotographicVideoGuide, videoBytesSha256, type PhotographicGuide } from './PhotographicVideoGuide';
import { preparePhotographicVideo } from './videoPhotographicWorkflow';
import { VideoRouteEditor } from './VideoRouteEditor';
import { useAuthStore } from '@/store';
import type { Building, SiteZone } from '@/types';
import { getCommunity3DCaptureClaims } from '@/features/community3d/community3d';
import { getCurrentResidualLandscapeClaim } from './globe/residualLandscape';
import {
  DEFAULT_VIDEO_ROUTE,
  DEFAULT_STREET_VIDEO_ROUTE,
  routeSignature,
  type VideoRoutePoint,
} from './videoRenderPath';
import { buildVideoSceneContract } from './videoSceneContract';
import { useVideoRoutePreview } from './useVideoRoutePreview';
import {LocalVideoPreview} from './LocalVideoPreview';
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
  { id: 'path_follow', name: 'Aerial', detail: 'Slow + high oblique' },
  { id: 'street_walkby', name: 'Street', detail: 'Slow + pedestrian height' },
  { id: 'detail_flythrough', name: 'Low detail fly-through', detail: '6 m · between buildings' },
  { id: 'bicycle_ride', name: 'Bicycle ride', detail: '1.6 m · forward view · up to 56 m' },
  { id: 'people_follow', name: 'Follow a person', detail: '1.6 m · tracks the first placed person' },
] as const;

type MotionId = typeof MOTIONS[number]['id'];
type VideoProvider = 'omni' | 'seedance_mini' | 'internal_enhance';
type SeedanceReferenceMode = 'preview_only' | 'preview_plus_keyframes';
type InternalEnhanceQuality = 'fast' | 'gpu_detail';

function providerName(provider?: VideoProvider | 'kling' | 'comfyui'): string {
  if (provider === 'comfyui') return 'Wan · local';
  if (provider === 'kling') return 'Kling';
  if (provider === 'seedance_mini') return 'Seedance Mini';
  if (provider === 'internal_enhance') return 'Internal Enhance';
  return 'Omni';
}

function providerSlug(provider?: VideoProvider | 'kling' | 'comfyui'): string {
  if (provider === 'comfyui') return 'comfy-animation';
  if (provider === 'kling') return 'kling-animation';
  if (provider === 'seedance_mini') return 'seedance-mini';
  if (provider === 'internal_enhance') return 'internal-enhance';
  return 'omni';
}

function providerOrigin(provider?: VideoProvider | 'kling' | 'comfyui'): string {
  if (provider === 'comfyui') return 'Local ComfyUI · animated still';
  if (provider === 'kling') return 'fal Kling · animated still';
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
  provider?: VideoProvider | 'kling' | 'comfyui';
  mode?: 'route_video' | 'saved_render_animation';
  source_render_id?: string | null;
  scene_direction?: string | null;
  recoverable?: boolean;
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
  output_media?: { width: number; height: number; fps: number; frame_count: number; duration_seconds: number } | null;
  media_warning?: string | null;
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
  if (attempt.mode === 'saved_render_animation') return `${providerName(attempt.provider)} · animated still · slow push-in`;
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
  allowance_scope?: 'provider' | 'trial';
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
  allowance_scope?: 'provider' | 'trial';
  estimated_cost_usd: number;
  video_credit_cost?: number;
  photographic_guide_credit_cost?: number;
  total_credit_cost?: number;
  model: string;
  reference_image_count: number;
  scene_revision_sha256: string;
}

interface VideoCaptureProfile {
  encoder: 'webcodecs_h264' | 'media_recorder_webm';
  fixed_timestep: true;
  frame_count: 96 | 192;
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
  duration_seconds: 4 | 8;
  character_reference_base64?: string;
  character_reference_mime_type?: 'image/png' | 'image/jpeg';
  omni_reference_mode?: 'video_only' | 'architecture_references' | 'appearance_references';
  appearance_attempt_id?: string;
  custom_prompt: string;
  use_custom_prompt_only: boolean;
  scene_brief: string;
  details_revision?: number;
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
  peopleDirection?: string;
  detailsRevision?: number;
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
  peopleDirection = '',
  detailsRevision,
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
  const [routePoints, setRoutePoints] = useState<VideoRoutePoint[]>(() => [...DEFAULT_VIDEO_ROUTE]);
  const [motion, setMotion] = useState<MotionId>('path_follow');
  const [videoGenerationEnabled, setVideoGenerationEnabled] = useState(false);
  // New clips always use Omni route editing; the wider types keep saved history readable.
  const [provider] = useState<VideoProvider>('omni');
  const [seedanceReferenceMode] = useState<SeedanceReferenceMode>('preview_plus_keyframes');
  const [useSceneReferences, setUseSceneReferences] = useState(false);
  const [usePhotographicFinish, setUsePhotographicFinish] = useState(true);
  const [photographicGuide, setPhotographicGuide] = useState<PhotographicGuide | null>(null);
  const [isPreparingGuide, setIsPreparingGuide] = useState(false);
  const [recoveredAppearance, setRecoveredAppearance] = useState<{ request: PreparedVideoRequest; signature: string } | null>(null);
  const [pendingAppearanceRestore, setPendingAppearanceRestore] = useState<{request: PreparedVideoRequest; guide: PhotographicGuide} | null>(null);
  const [internalEnhanceQuality] = useState<InternalEnhanceQuality>('fast');
  const [renderQuality, setRenderQuality] = useState<VideoRenderQuality>('draft');
  const [controlMode] = useState<VideoControlMode>('preview_video');
  const [routeEditing, setRouteEditing] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [useCustomPromptOnly, setUseCustomPromptOnly] = useState(false);
  const [duration, setDuration] = useState<4 | 8>(8);
  const [animatePeople, setAnimatePeople] = useState(true);
  const [characterReference, setCharacterReference] = useState<{ dataUrl: string; mimeType: 'image/png' | 'image/jpeg'; name: string; revision: number } | null>(null);
  const [referenceLoading, setReferenceLoading] = useState(false);
  const referenceSequence = useRef(0);
  const [preparedSignature, setPreparedSignature] = useState<string | null>(null);
  const supportsPeopleEdit = provider === 'omni' && controlMode === 'preview_video';
  const durationSeconds = supportsPeopleEdit ? duration : 8;
  const [sourceCaptureVersion, setSourceCaptureVersion] = useState(0);
  const [previewProgress, setPreviewProgress] = useState('Preparing your route…');
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
    () => `${sceneClaimsSignature(community3DClaims, residualLandscapeClaim)}:${detailsRevision ?? ""}:${peopleDirection}`,
    [community3DClaims, residualLandscapeClaim, detailsRevision, peopleDirection],
  );
  const routeCaptureSignature = useMemo(
    () => `${projectId}:${sourceCaptureVersion}:${renderQuality}:${motion}:${durationSeconds}:${animatePeople}:${routeSignature(routePoints)}:${sceneContract.signature}:${currentSceneRevisionSignature}`,
    [projectId, sourceCaptureVersion, motion, renderQuality, durationSeconds, animatePeople, routePoints, sceneContract.signature, currentSceneRevisionSignature],
  );

  const { routeControls, setRouteControls, isPreparingControls, isCancelling, cancel:cancelRoutePreview, prepare: prepareRoutePreview } = useVideoRoutePreview(routeCaptureSignature);
  const freeCheckRun=useRef(0);
  useEffect(()=>()=>{freeCheckRun.current++;},[]);
  const appearanceSignature = `${routeCaptureSignature}:${customPrompt.trim()}`;
  useEffect(() => {
    if (!pendingAppearanceRestore) return;
    const request = pendingAppearanceRestore.request;
    setRecoveredAppearance({ request, signature: appearanceSignature });
    setPhotographicGuide({ ...pendingAppearanceRestore.guide, signature: appearanceSignature });
    setRouteControls({ signature: routeCaptureSignature, keyframesBase64: [request.guide_frame_base64],
      previewVideoBase64: request.preview_video_base64!, previewVideoMimeType: request.preview_video_mime_type! });
    setPendingAppearanceRestore(null);
  }, [pendingAppearanceRestore, appearanceSignature, routeCaptureSignature, setRouteControls]);
  const restoreAppearanceSource = useCallback((source: unknown, guide: PhotographicGuide) => {
    const request = source as PreparedVideoRequest;
    if (request?.project_id !== projectId || request.provider !== 'omni' || request.control_mode !== 'preview_video'
      || !request.preview_video_base64 || !request.route_points?.length) {
      setError('The saved original route could not be restored. No video was requested.'); return;
    }
    setMotion(request.camera_motion); setDuration(request.duration_seconds); setRenderQuality(request.render_quality);
    setRoutePoints(request.route_points); setSourceFrame(request.guide_frame_base64);
    ++referenceSequence.current; setCharacterReference(null);
    setCustomPrompt(request.custom_prompt); setSourceCaptureVersion(v => v + 1);
    setPreflight(null); setPrepared(null); setPendingAppearanceRestore({request, guide});
  }, [projectId]);

  const currentSignature = useMemo(
    () => `${provider}:${seedanceReferenceMode}:${internalEnhanceQuality}:${renderQuality}:${controlMode}:${motion}:${routeCaptureSignature}:${sceneContract.signature}:${currentSceneRevisionSignature}:${supportsPeopleEdit ? customPrompt.trim() : ''}:${supportsPeopleEdit && useCustomPromptOnly}:${supportsPeopleEdit ? characterReference?.revision ?? 0 : 0}:${supportsPeopleEdit && useSceneReferences}:${supportsPeopleEdit && usePhotographicFinish}`,
    [controlMode, currentSceneRevisionSignature, customPrompt, useCustomPromptOnly, internalEnhanceQuality, motion, provider, renderQuality, routeCaptureSignature, sceneContract.signature, seedanceReferenceMode, supportsPeopleEdit, characterReference, useSceneReferences, usePhotographicFinish],
  );
  const latestSignature = useRef(currentSignature);
  latestSignature.current = currentSignature;
  const submission = useRef<{ body: PreparedVideoRequest; signature: string | null; requestId: string } | null>(null);
  const submissionInFlight = useRef(false);
  const hasValidCost = typeof preflight?.estimated_cost_usd === 'number'
    && Number.isFinite(preflight.estimated_cost_usd) && preflight.estimated_cost_usd >= 0;
  const hasValidPreflight = Boolean(preflight?.ready && hasValidCost && preparedSignature === currentSignature);
  const providerUsage = pilot.provider_usage[provider];
  const providerCanRun = videoGenerationEnabled && (providerUsage.attempts_remaining === null
    || providerUsage.attempts_remaining > 0);

  const selectCharacterReference = async (file?: File) => {
    const sequence = ++referenceSequence.current;
    setPreflight(null); setPrepared(null); setCharacterReference(null);
    if (!file) { setReferenceLoading(false); return; }
    setReferenceLoading(true);
    try {
      if (!['image/png', 'image/jpeg'].includes(file.type) || file.size > 8 * 1024 * 1024) {
        throw new Error('Choose a PNG or JPEG character image smaller than 8 MB.');
      }
      const dataUrl = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = () => reject(new Error('The character image could not be read.'));
        reader.readAsDataURL(file);
      });
      const image = await loadImage(dataUrl);
      if (!image.naturalWidth || !image.naturalHeight || Math.max(image.naturalWidth, image.naturalHeight) > 4096) {
        throw new Error('The character image must be no larger than 4096 pixels on either side.');
      }
      if (sequence === referenceSequence.current) setCharacterReference({ dataUrl, mimeType: file.type as 'image/png' | 'image/jpeg', name: file.name, revision: sequence });
    } catch (cause) {
      if (sequence === referenceSequence.current) setError(cause instanceof Error ? cause.message : 'The character image could not be prepared.');
    } finally {
      if (sequence === referenceSequence.current) setReferenceLoading(false);
    }
  };

  const loadPilot = useCallback(async () => {
    setVideoGenerationEnabled(false);
    try {
      const capabilities = await direct3DAttempts.capabilities();
      setVideoGenerationEnabled(capabilities.video_enabled === true);
      if (capabilities.video_enabled !== true) return;
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
        setSourceCaptureVersion(version => version + 1);
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
  }, [canvas, captureAerialFrame, onBeforeCapture, renderQuality, waitForTilesSettled, setRouteControls]);

  const selectMotion = useCallback((nextMotion: MotionId) => {
    setMotion(nextMotion);
    if (nextMotion === 'people_follow') setAnimatePeople(true);
    setRouteControls(null);
    setRoutePoints([...(nextMotion === 'path_follow' ? DEFAULT_VIDEO_ROUTE : DEFAULT_STREET_VIDEO_ROUTE)]);
    setRouteEditing(false);
    setPreflight(null);
    setPrepared(null);
  }, [setRouteControls]);

  useEffect(() => {
    void loadPilot();
  }, [loadPilot]);

  useEffect(() => {
    if (!captureStarted.current) {
      captureStarted.current = true;
      void capture();
    }
  }, [capture]);

  useEffect(() => {
    if (preparedSignature && preparedSignature !== currentSignature) {
      setPreflight(null);
      setPrepared(null);
    }
  }, [currentSignature, preparedSignature]);

  const prepareLocalPreview = useCallback(async () => {
    if (!sourceFrame) throw new Error('Capture the scene before preparing a preview.');
    if (routePoints.length < 2) throw new Error('Draw a route with a start and finish.');
    if (!community3DClaims || (community3DClaims.length === 0 && detailsRevision === undefined)) {
      throw new Error(isCatalogueOnlyScene(siteZones) ? CATALOGUE_UPDATE_GUIDANCE : 'The 3D scene changed. Close Video Render and update the 3D scene before trying again.');
    }
    if (!captureRouteControls) throw new Error('This 3D view cannot prepare a video preview yet.');
    return prepareRoutePreview(async (signal) => {
      setPreviewProgress('Preparing your route…');
      const captured = await captureRouteControls({
        signal,
        routePoints, cameraMotion: motion, renderQuality, durationSeconds, animatePeople, keyframeCount: 6,
        automaticRoute: motion === 'street_walkby' && routeSignature(routePoints) === routeSignature(DEFAULT_STREET_VIDEO_ROUTE),
        onProgress: (phase, completed, total) => setPreviewProgress(`${phase === 'loading' ? 'Loading the surroundings' : phase === 'checking' ? 'Checking route views' : 'Creating your preview'} · ${Math.round(completed / total * 100)}%`),
      });
      const normalizedKeyframes = await Promise.all(captured.keyframesBase64.map(frame => normalizeImageFrame(
        frame.startsWith('data:') ? frame : `data:image/png;base64,${frame}`, renderQuality,
      )));
      signal.throwIfAborted();
      return { ...captured, keyframesBase64: normalizedKeyframes };
    }, controlMode === 'multi_keyframe' ? 2 : provider === 'seedance_mini' && seedanceReferenceMode === 'preview_plus_keyframes' ? 3 : 1);
  }, [sourceFrame, routePoints, community3DClaims, detailsRevision, siteZones, captureRouteControls, prepareRoutePreview, motion, renderQuality, durationSeconds, animatePeople, controlMode, provider, seedanceReferenceMode]);

  const previewLocally = useCallback(async () => {
    setError(null);
    try { await prepareLocalPreview(); }
    catch (previewError) { if((previewError as Error)?.name!=='AbortError')setError(getApiErrorMessage(previewError, 'The preview could not be prepared. Try again when the scene is ready.')); }
  }, [prepareLocalPreview]);

  const cancelFreePreview=useCallback(async()=>{
    freeCheckRun.current++;
    setIsPreflighting(false);setPreflight(null);setPrepared(null);setError(null);
    setPreviewProgress('Cancelling preview…');
    await cancelRoutePreview();
  },[cancelRoutePreview]);
  const closePanel=useCallback(async()=>{
    if(isGenerating)return;
    await cancelFreePreview();
    onClose();
  },[isGenerating,cancelFreePreview,onClose]);
  useEffect(()=>{
    const escape=(event:KeyboardEvent)=>{
      if(event.key!=='Escape'||isGenerating)return;
      event.preventDefault();event.stopImmediatePropagation();void closePanel();
    };
    window.addEventListener('keydown',escape,true);
    return()=>window.removeEventListener('keydown',escape,true);
  },[closePanel,isGenerating]);

  const requestBody = useCallback(async (includePhotographicGuide = true): Promise<PreparedVideoRequest> => {
    if (!sourceFrame) throw new Error('Capture the scene before validating.');
    if (routePoints.length < 2) throw new Error('Draw a route with a start and finish.');
    if (!community3DClaims || (community3DClaims.length === 0 && detailsRevision === undefined)) {
      throw new Error(isCatalogueOnlyScene(siteZones) ? CATALOGUE_UPDATE_GUIDANCE : 'The 3D scene changed. Close Video Render and update the 3D scene before trying again.');
    }
    if (supportsPeopleEdit && usePhotographicFinish && recoveredAppearance?.signature === appearanceSignature) {
      if (includePhotographicGuide && (!photographicGuide || photographicGuide.signature !== appearanceSignature)) {
        throw new Error('Review the matching photographic guide first.');
      }
      return { ...recoveredAppearance.request,
        character_reference_base64: characterReference?.dataUrl,
        character_reference_mime_type: characterReference?.mimeType,
        route_keyframes_base64: includePhotographicGuide ? [`data:image/png;base64,${photographicGuide!.image_base64}`] : [],
        omni_reference_mode: includePhotographicGuide ? 'appearance_references' : 'video_only',
        appearance_attempt_id: includePhotographicGuide ? photographicGuide!.attempt_id : undefined,
        use_custom_prompt_only: includePhotographicGuide || recoveredAppearance.request.use_custom_prompt_only,
        scene_brief: withPeopleDirection(recoveredAppearance.request.scene_brief || sceneContract.text, peopleDirection),
        custom_prompt: customPrompt.trim() || 'Make this exact scene look like a live-action architectural film with realistic people and materials. Clear blue sky, soft clouds and neutral sunshine.' };
    }
    const activeControls = controlMode !== 'single_frame' ? await prepareLocalPreview() : null;
    if (activeControls?.previewCaptureProfile?.frameCount !== undefined
      && activeControls.previewCaptureProfile.frameCount !== durationSeconds * 24) {
      throw new Error('The source frame count does not match the selected clip length. Prepare the route again.');
    }

    const sceneBrief = provider === 'internal_enhance'
      ? `${sceneContract.text}\nSOURCE POLICY: The deterministic City Prompt route preview already contains the approved render-locked GLB skins, open-space assets, context buildings, and exact camera timing. Restore only detail present in those pixels. Do not synthesize or reinterpret any object.`
      : controlMode === 'multi_keyframe'
      ? `${sceneContract.text}\nSOURCE POLICY: The ordered City Prompt route images are the only visual authorities. They depict one unchanged scene along the exact desired path. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`
      : controlMode === 'preview_video'
        ? `${sceneContract.text}\nSOURCE POLICY: The City Prompt route preview is the exact camera, geography, and geometry authority. Preserve every frame's layout, topology, context, and timing. Omni may improve only the physically plausible visual finish already implied by the source; it must not redesign or relocate anything.`
        : `${sceneContract.text}\nSOURCE POLICY: Image1 is the only visual input. Animate the captured scene as-is. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`;
    const allRouteKeyframes = activeControls?.keyframesBase64 ?? [];
    // Keep architectural source admission on finished enhancement; a free
    // exact-camera preview may show a sparse park without inventing detail.
    if (motion !== 'path_follow' && allRouteKeyframes.length) await assertNearFieldVideoSourceQuality(allRouteKeyframes,
      {authoredPeople: (activeControls?.peopleCaptureCount ?? 0) > 0 && community3DClaims.length === 0});
    const appearanceReferences = supportsPeopleEdit && usePhotographicFinish && includePhotographicGuide;
    if (appearanceReferences && (!photographicGuide || photographicGuide.signature !== appearanceSignature)) {
      throw new Error('Create and review a photographic guide for this scene and route first.');
    }
    const architectureReferences = supportsPeopleEdit && useSceneReferences && !usePhotographicFinish;
    if (architectureReferences && !allRouteKeyframes.length) {
      throw new Error('Capture a route preview before using scene reference frames.');
    }
    const routeKeyframes = controlMode === 'multi_keyframe'
      ? allRouteKeyframes
      : appearanceReferences && photographicGuide
        ? [`data:image/png;base64,${photographicGuide.image_base64}`]
      : architectureReferences
        ? allRouteKeyframes.length === 1 ? allRouteKeyframes : [allRouteKeyframes[0], allRouteKeyframes[allRouteKeyframes.length - 1]]
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
      guide_frame_base64: allRouteKeyframes[0] ?? sourceFrame,
      control_mode: controlMode,
      route_keyframes_base64: routeKeyframes,
      ...(architectureReferences ? { omni_reference_mode: 'architecture_references' as const } : {}),
      ...(appearanceReferences && photographicGuide ? { omni_reference_mode: 'appearance_references' as const,
        appearance_attempt_id: photographicGuide.attempt_id } : {}),
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
          frame_count: (activeControls.previewCaptureProfile.frameCount ?? durationSeconds * 24) as 96 | 192,
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
      duration_seconds: durationSeconds,
      ...(supportsPeopleEdit && characterReference ? {
        character_reference_base64: characterReference.dataUrl,
        character_reference_mime_type: characterReference.mimeType,
      } : {}),
      custom_prompt: provider === 'omni' && controlMode === 'preview_video' ? customPrompt.trim() || (appearanceReferences ? 'Make this exact scene look like a live-action architectural film with realistic people and materials. Clear blue sky, soft clouds and neutral sunshine.' : '') : '',
      use_custom_prompt_only: provider === 'omni' && controlMode === 'preview_video' && (useCustomPromptOnly || appearanceReferences),
      scene_brief: withPeopleDirection(sceneBrief, peopleDirection),
      community_3d_claims: community3DClaims,
      details_revision: detailsRevision,
      ...(residualLandscapeClaim ? {
        residual_landscape_claim: residualLandscapeClaim,
      } : {}),
    };
  }, [peopleDirection, prepareLocalPreview, community3DClaims, customPrompt, useCustomPromptOnly, detailsRevision, controlMode, internalEnhanceQuality, motion, projectId, provider, renderQuality, residualLandscapeClaim, routePoints, sceneContract, seedanceReferenceMode, sourceFrame, siteZones, durationSeconds, supportsPeopleEdit, characterReference, useSceneReferences, usePhotographicFinish, photographicGuide, appearanceSignature, recoveredAppearance]);

  const prepareAppearance = useCallback(async () => {
    const body = await requestBody(false);
    // Validate the real route/scene before buying its still. This is free.
    const check = await videoRenderApi.preflight(body) as PreflightResult;
    if (!check.ready) throw new Error('Preview the current scene successfully before creating a photographic guide.');
    if (!body.preview_video_base64) throw new Error('Capture the free route preview first.');
    return { purpose: 'video_appearance' as const, project_id: projectId,
      beauty_image_base64: body.guide_frame_base64,
      source_video_sha256: await videoBytesSha256(body.preview_video_base64), prompt: customPrompt.trim(),
      details_revision: detailsRevision, community_3d_claims: body.community_3d_claims,
      residual_landscape_claim: body.residual_landscape_claim, source_request: body };
  }, [requestBody, projectId, customPrompt, detailsRevision]);

  const runPreflight = useCallback(async () => {
    const run=++freeCheckRun.current;
    setIsPreflighting(true);
    setError(null);
    try {
      const body = await requestBody(Boolean(photographicGuide?.signature === appearanceSignature));
      if(run!==freeCheckRun.current)return;
      const result = await videoRenderApi.preflight({...body,
        prepare_photographic_finish: usePhotographicFinish && !body.appearance_attempt_id}) as PreflightResult;
      if(run!==freeCheckRun.current)return;
      if (latestSignature.current !== currentSignature) throw new Error('The scene changed during the free check. Preview the current scene again.');
      if (!result.ready || typeof result.estimated_cost_usd !== 'number' || !Number.isFinite(result.estimated_cost_usd) || result.estimated_cost_usd < 0) {
        throw new Error('The free check did not return a valid cost quote. Preview again before generating.');
      }
      setPrepared(body);
      setPreparedSignature(currentSignature);
      setPreflight(result);
      setPilot((current) => ({
        ...current,
        provider_usage: {
          ...current.provider_usage,
          [result.provider]: {
            attempts_used: result.attempts_used,
            attempts_remaining: result.attempts_remaining,
            max_attempts: result.max_attempts,
            allowance_scope: result.allowance_scope,
          },
        },
      }));
      toast.success('Scene and route passed the zero-cost check');
    } catch (preflightError) {
      if(run!==freeCheckRun.current || (preflightError as Error)?.name==='AbortError')return;
      setPreflight(null);
      setPrepared(null);
      setError(getApiErrorMessage(preflightError, 'Video preflight failed.'));
    } finally {
      if(run===freeCheckRun.current)setIsPreflighting(false);
    }
  }, [requestBody, currentSignature, photographicGuide, appearanceSignature, usePhotographicFinish]);

  const generate = useCallback(async () => {
    if (!prepared || !hasValidPreflight || !providerCanRun || isPreparingGuide || submissionInFlight.current) return;
    submissionInFlight.current = true;
    // An uncertain response can already have reserved a paid attempt. A free
    // recheck of unchanged inputs must replay that same request, never buy twice.
    const requestingUserId = useAuthStore.getState().user?.id;
    setIsGenerating(true);
    setError(null);
    try {
      if (submission.current?.signature !== preparedSignature) {
        let body = prepared;
        if (usePhotographicFinish && !body.appearance_attempt_id) {
          setIsPreparingGuide(true);
          const request = {purpose:'video_appearance' as const,project_id:projectId,
            beauty_image_base64:body.guide_frame_base64,
            source_video_sha256:await videoBytesSha256(body.preview_video_base64!),
            prompt:customPrompt.trim(),details_revision:detailsRevision,
            community_3d_claims:body.community_3d_claims,residual_landscape_claim:body.residual_landscape_claim,
            source_request:body};
          const existing = photographicGuide?.signature === appearanceSignature ? photographicGuide : null;
          const guide = existing ?? await preparePhotographicVideo(direct3DAttempts,request,preflight!.scene_revision_sha256);
          // Save a paid guide even when the scene changed while awaiting it.
          setPhotographicGuide({...guide,signature:appearanceSignature});
          if (latestSignature.current !== preparedSignature) throw new Error('The scene changed. Your photographic guide is saved; preview the current scene before continuing.');
          body={...body,omni_reference_mode:'appearance_references',appearance_attempt_id:guide.attempt_id,
            route_keyframes_base64:[`data:image/png;base64,${guide.image_base64}`],
            use_custom_prompt_only:true,custom_prompt:body.custom_prompt || 'Make this exact scene look like a live-action architectural film with realistic people and materials. Clear blue sky, soft clouds and neutral sunshine.'};
          const bound = await videoRenderApi.preflight(body) as PreflightResult;
          if (!bound.ready || !Number.isFinite(bound.estimated_cost_usd) || bound.estimated_cost_usd < 0
            || bound.estimated_cost_usd > preflight!.estimated_cost_usd || bound.scene_revision_sha256 !== preflight!.scene_revision_sha256 || latestSignature.current !== preparedSignature) {
            throw new Error('The scene or video quote changed. Your photographic guide is saved; preview again before continuing.');
          }
          setPreflight(bound);
        }
        submission.current = {body,signature:preparedSignature,requestId:crypto.randomUUID()};
      }
      const result = await videoRenderApi.generate({
        ...submission.current!.body,
        request_id: submission.current!.requestId,
        confirm_paid_submission: true,
      }) as { attempt: VideoAttempt; attempts_used: number; attempts_remaining: number | null };
      submission.current = null;
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
      submissionInFlight.current = false;
      setIsPreparingGuide(false);
      setIsGenerating(false);
      // A failed/uncertain response may still have reserved a paid call. Refresh
      // server accounting without hiding saved video or restoring a signed-out user.
      if (requestingUserId) void authApi.me().then(user => {
        if (user.id === requestingUserId && useAuthStore.getState().user?.id === requestingUserId) {
          useAuthStore.getState().setUser(user);
        }
      }).catch(() => { /* Reconciled on the next account refresh. */ });
    }
  }, [hasValidPreflight, loadPilot, onVideoSaved, prepared, preparedSignature, providerCanRun, isPreparingGuide,
    usePhotographicFinish,projectId,customPrompt,detailsRevision,photographicGuide,appearanceSignature,preflight]);

  const changeRoute = (points: VideoRoutePoint[]) => {
    setRoutePoints(points); setRouteControls(null); setPreflight(null); setPrepared(null);
    setPhotographicGuide(null); setRecoveredAppearance(null); setError(null);
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
            <p className="truncate text-[11px] text-white/55">Omni 1.1 · Choose a shot, preview, then generate.</p>
          </div>
          {videoGenerationEnabled ? <div className="ml-auto hidden items-center gap-2 rounded-full border border-white/15 bg-white/[0.06] px-3 py-1.5 sm:flex">
            <span className="text-[10px] font-bold uppercase tracking-wider text-white/50">Videos used</span>
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
          </div> : <span className="ml-auto text-xs font-bold text-white/70">Free route preview</span>}
          <button onClick={()=>void closePanel()} disabled={isGenerating || isCancelling} className="rounded-full p-2 text-white/60 transition hover:bg-white/10 hover:text-white disabled:opacity-30" aria-label="Close Video Render">
            <X size={19} />
          </button>
        </header>

        <div className="grid min-h-0 flex-1 overflow-y-auto lg:grid-cols-[minmax(0,1.65fr)_minmax(330px,0.75fr)] lg:overflow-hidden">
          <section className="flex min-h-[430px] flex-col border-b-2 border-[#151515] bg-[#0d1718] p-3 lg:min-h-0 lg:overflow-y-auto lg:border-b-0 lg:border-r-2 lg:p-5">
            <div className="mb-3 flex flex-wrap items-center gap-2 text-white">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-[10px] font-black uppercase tracking-wider">
                <MapPinned size={12} /> Camera journey
              </span>
              <span className="text-[11px] text-white/65">{motion === 'people_follow' ? 'The camera follows the first animated person and their saved action automatically.' : 'Draw a journey on this captured site view.'}</span>
              {motion !== 'people_follow' && <>
                <button type="button" onClick={() => setRouteEditing(true)} disabled={isGenerating || isPreparingControls || isPreflighting}
                  className="ml-auto min-h-10 rounded-full border border-white/30 px-3 text-xs">{routePoints.length ? 'Edit route' : 'Draw route'}</button>
                <button type="button" onClick={() => {changeRoute([]); setRouteEditing(false);}} disabled={isGenerating || isPreparingControls || isPreflighting || !routePoints.length}
                  className="min-h-10 rounded-full border border-white/30 px-3 text-xs">Delete route</button>
              </>}
            </div>

            <div className="relative aspect-video w-full shrink-0 overflow-hidden rounded-2xl border border-white/15 bg-black shadow-2xl">
              {sourceFrame && <img src={sourceFrame} alt="Captured City Prompt scene" className="absolute inset-0 h-full w-full select-none object-cover" draggable={false} />}
              {isCapturing && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#111c1d] text-sm font-semibold text-white/65">
                  <Loader2 className="mr-2 animate-spin" size={18} /> Capturing clean 16:9 scene…
                </div>
              )}
              {isPreparingControls && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-[#111c1d]/90 px-8 text-center text-sm font-semibold text-white/75">
                  <Loader2 className="mb-3 animate-spin" size={24} />
                  <span role="status" aria-live="polite">{previewProgress}</span>
                  <span className="mt-1 text-[10px] font-normal text-white/45">Rendering the exact route can take several minutes on a laptop. No provider call or credit is used.</span>
                </div>
              )}
              {!isCapturing && !sourceFrame && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 px-8 text-center text-sm text-white/60">
                  <Film size={28} />
                  <span>The scene could not be captured.</span>
                  <button onClick={() => void capture()} className="rounded-full bg-white px-4 py-2 text-xs font-black uppercase text-[#151515]">Try capture again</button>
                </div>
              )}
              {sourceFrame && routeEditing && motion !== 'people_follow' && <VideoRouteEditor points={routePoints}
                onChange={changeRoute} onClose={() => setRouteEditing(false)} disabled={isGenerating || isPreparingControls || isPreflighting || isCapturing} />}
              <div className="pointer-events-none absolute bottom-3 left-3 rounded-full bg-black/65 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-white/75 backdrop-blur">
                16:9 · {videoRenderQualityProfile(renderQuality).outputHeight}p · {durationSeconds} sec · {durationSeconds * 24} fixed frames
              </div>
              {motion === 'street_walkby' && (
                <div className="pointer-events-none absolute right-3 top-3 rounded-full border border-[#c9ff3d]/50 bg-[#0d1718]/85 px-3 py-1.5 text-[9px] font-black uppercase tracking-wider text-[#c9ff3d] backdrop-blur">
                  City Prompt authored renderer
                </div>
              )}
            </div>

            {recoveredAppearance?.signature === appearanceSignature && <p className="mt-2 rounded-lg border border-white/20 p-2 text-xs text-white">Using the original saved route recording. Its exact camera and motion are restored; change the route or recapture the scene to make a new source.</p>}

            {routeControls?.signature === routeCaptureSignature && (
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
                ) : null}
                <LocalVideoPreview source={routeControls.previewVideoBase64} mimeType={routeControls.previewVideoMimeType} showPlayer={controlMode!=='multi_keyframe'}/>
                {routeControls.routeProfile && <p className="mt-2 text-xs text-white/70">{routeControls.routeProfile.distanceMeters.toFixed(1)} m route · {(routeControls.routeProfile.averageSpeedMps * 3.6).toFixed(1)} km/h average{routeControls.routeProfile.eyeHeightMeters ? ` · ${routeControls.routeProfile.eyeHeightMeters} m camera height` : ''}</p>}
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
                    <span className="uppercase text-[#c9ff3d]">{renderQuality === 'high' ? 'High-quality source' : 'Draft source'}</span>
                    <span>{routeControls.previewCaptureProfile.renderWidth}×{routeControls.previewCaptureProfile.renderHeight} render</span>
                    <span>→ {routeControls.previewCaptureProfile.width}×{routeControls.previewCaptureProfile.height}</span>
                    <span>{routeControls.previewCaptureProfile.tileWarmupFrameCount ?? 0} tile-preload poses</span>
                    {routeControls.geometryPassProfile && (
                      <span>{routeControls.geometryPassProfile.depthCheckpointCount}/{routeControls.geometryPassProfile.checkpointCount} depth + normal checkpoints</span>
                    )}
                  </div>
                )}
                {routeControls.renderStats && <details className="mt-2 text-[10px] text-white/60"><summary>Preview measurements</summary>
                  <p>{routeControls.peopleCaptureCount ?? 0} animated people · {routeControls.previewCaptureProfile?.frameCount} frames · {routeControls.renderStats.drawCalls} draw calls · {routeControls.renderStats.triangles.toLocaleString()} triangles</p>
                  <p>{routeControls.renderStats.geometries} geometries · {routeControls.renderStats.textures} textures · CPU submission median {routeControls.renderStats.cpuSubmissionMedianMs.toFixed(1)} ms · p95 {routeControls.renderStats.cpuSubmissionP95Ms.toFixed(1)} ms. GPU and encoding time are additional.</p>
                </details>}
              </div>
            )}


          </section>

          <aside className="flex min-h-0 flex-col bg-[#f7f2e8] lg:overflow-y-auto">
            <div className="space-y-4 p-4 sm:p-5">
              {!videoGenerationEnabled && <p role="status" className="rounded-lg border border-slate-300 bg-white p-3 text-sm">Finished video generation is unavailable on this server. Preview the current view locally and download the exact 3D journey for free.</p>}
              <fieldset disabled={isGenerating || isPreparingControls || isPreflighting || isPreparingGuide}>
                <legend className="mb-2 text-sm font-black">1. Choose a shot</legend>
                <div className="grid grid-cols-3 gap-2">
                  {MOTIONS.filter(item => ['path_follow', 'street_walkby', 'people_follow'].includes(item.id)).map(item => (
                    <button key={item.id} type="button" aria-pressed={motion === item.id} onClick={() => selectMotion(item.id)}
                      className={`min-h-14 rounded-xl border-2 px-2 py-2 text-xs font-bold ${motion === item.id ? 'border-[#151515] bg-[#c9ff3d]' : 'border-[#151515]/20 bg-white'}`}>
                      {item.name}
                    </button>
                  ))}
                </div>
              </fieldset>
              <div>
                <label htmlFor="video-custom-prompt" className="mb-1 block text-xs font-bold text-[#151515]">Custom prompt (optional)</label>
                <textarea id="video-custom-prompt" value={customPrompt} maxLength={600} rows={3}
                  disabled={isGenerating || isPreflighting}
                  onChange={event => { setCustomPrompt(event.target.value); setPreflight(null); setPrepared(null); }}
                  placeholder="A woman walks her dog along the existing sidewalk."
                  className="w-full resize-y rounded-xl border border-[#151515]/25 bg-white p-3 text-sm text-[#151515] focus:border-[#151515] focus:ring-2 focus:ring-[#c9ff3d] disabled:opacity-50" />
                <p className="mt-1 text-[10px] text-[#151515]/60">Keep it to one clear appearance or activity detail. The building massing, street layout and camera route should stay recognizable.</p>
              </div>
              <label className="mb-2 flex items-center gap-2 text-xs font-bold text-[#151515]">
                <input type="checkbox" checked={usePhotographicFinish} disabled={isGenerating || isPreflighting || isPreparingGuide}
                  onChange={event => { setUsePhotographicFinish(event.target.checked); setPreflight(null); setPrepared(null); }} className="accent-[#96ba10]" />
                Photographic finish
              </label>
              {usePhotographicFinish && <PhotographicVideoGuide automatic disabled={isGenerating || isPreflighting || isPreparingControls} projectId={projectId} signature={appearanceSignature}
                guide={photographicGuide} prepare={prepareAppearance} onChange={guide => {setPhotographicGuide(guide); setPreflight(null); setPrepared(null);}} onBusyChange={setIsPreparingGuide} onRestoreSource={restoreAppearanceSource} />}
              <details className="rounded-xl border border-[#151515]/20 p-3">
                <summary className="cursor-pointer text-sm font-bold">Advanced</summary>
                <div className="mt-3 space-y-4">
                <label className="flex items-center gap-2 text-xs font-bold">
                  <input type="checkbox" checked={routeEditing} disabled={isGenerating || isPreparingControls || isPreflighting}
                    onChange={event => setRouteEditing(event.target.checked)} /> Edit route on preview
                </label>
                <div className="flex gap-2">{MOTIONS.filter(item => ['bicycle_ride', 'detail_flythrough'].includes(item.id)).map(item => (
                  <button type="button" key={item.id} aria-pressed={motion === item.id} onClick={() => selectMotion(item.id)} disabled={isGenerating || isPreparingControls || isPreflighting}
                    className="min-h-10 rounded-lg border px-2 text-xs">{item.name}</button>
                ))}</div>
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
                  <div className="mb-2 flex items-center justify-between">
                    <p className="text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Scene lock</p>
                    <span className="inline-flex items-center gap-1 rounded-full bg-[#fff0bf] px-2 py-1 text-[9px] font-black uppercase text-[#705000]"><ShieldCheck size={11} /> Continuity constrained</span>
                  </div>
                  <div className="rounded-xl border border-[#151515]/15 bg-white/65 p-3">
                    <p className="text-xs font-black leading-relaxed text-[#151515]/80">{sceneContract.summary}</p>
                    <p className="mt-1 text-[10px] font-semibold leading-relaxed text-[#151515]/55">
                      {provider === 'omni' && controlMode === 'preview_video'
                        ? 'The source guides the camera and layout. Omni targets live-action architectural footage with lifelike materials, lighting and planting. Optional scene details can add activity. Review every result for design changes.'
                        : 'The captured pixels lock authored massing, roofs, courtyards, facade rhythm, materials, lighting, Google context buildings, and open-space program. City Prompt adds no moving traffic or pedestrians; any baked Google context remains part of the captured surroundings.'}
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
                          ? 'Omni 1.1 edits the exact route recording. High quality requests 1080p output (Google upscales it); inspect the saved video’s actual resolution.'
                          : 'Omni receives one authoritative image plus conservative camera-motion instructions.'}
                    </p>
                    <p className="mt-2 rounded-lg bg-[#fff0bf] px-2 py-1.5 text-[9px] font-bold leading-relaxed text-[#705000]">
                      {provider === 'internal_enhance'
                        ? 'No scene generation: this pass only denoises, sharpens, stabilizes tone, and optionally super-resolves detail already present. The fidelity gate still checks every saved result.'
                        : `AI concept visualization: ${providerName(provider)} can still reinterpret geometry between frames. Verify the video against the 3D scene before using it for design decisions.`}
                    </p>
                  </div>
                  {provider === 'omni' && controlMode === 'preview_video' && (
                    <div className="mt-3">
                      <fieldset disabled={isGenerating || isPreflighting || isPreparingControls} className="mb-3 rounded-xl border border-[#151515]/15 p-3 text-[#151515]">
                        <legend className="px-1 text-xs font-bold">Clip length</legend>
                        <div className="flex gap-2">{([4, 8] as const).map(seconds => <button type="button" key={seconds}
                          aria-pressed={duration === seconds} onClick={() => setDuration(seconds)}
                          className={`min-h-10 flex-1 rounded-lg border border-[#151515] text-xs font-bold ${duration === seconds ? 'bg-[#c9ff3d]' : 'bg-white'}`}>{seconds} seconds</button>)}</div>
                        <label className="mt-3 flex items-center gap-2 text-xs font-bold">
                          <input type="checkbox" checked={animatePeople} disabled={motion === 'people_follow'} onChange={event => setAnimatePeople(event.target.checked)} className="accent-[#96ba10]" />
                          Animate placed people
                        </label>
                        <p className="mt-1 text-[10px] text-[#151515]/60">Uses the saved actions of placed people during capture. Moving people need a clear path; normal editing stays still.</p>
                      </fieldset>

                      <label className="mb-1 flex items-center gap-2 text-xs font-bold text-[#151515]">
                        <input type="checkbox" checked={useSceneReferences}
                          disabled={isGenerating || isPreflighting || usePhotographicFinish}
                          onChange={event => { setUseSceneReferences(event.target.checked); setPreflight(null); setPrepared(null); }}
                          className="accent-[#96ba10]" />
                        Use scene reference frames
                      </label>
                      <p className="mb-3 text-[10px] text-[#151515]/60">Adds up to two captured views to guide buildings and skyline. The source video still controls camera and motion. Fidelity remains approximate.</p>
                      <label htmlFor="video-character-reference" className="mb-1 block text-xs font-bold text-[#151515]">Character appearance reference (optional)</label>
                      <input id="video-character-reference" type="file" accept="image/png,image/jpeg" disabled={isGenerating || isPreflighting || referenceLoading}
                        onChange={event => void selectCharacterReference(event.target.files?.[0])}
                        className="w-full rounded-lg border border-[#151515]/25 bg-white p-2 text-xs text-[#151515] file:mr-2 file:rounded file:border-0 file:bg-[#e8f6bc] file:p-2" />
                      <p className="mt-1 text-[10px] text-[#151515]/60">A PNG/JPEG up to 8 MB and 4096 px. Guides appearance only; the route video controls motion and layout.</p>
                      {characterReference && <div className="my-2 flex items-center gap-2 text-xs text-[#151515]">
                        <img src={characterReference.dataUrl} alt="Character appearance reference" className="h-20 w-20 rounded-lg border object-contain" />
                        <span className="min-w-0 flex-1 truncate">{characterReference.name}</span>
                        <button type="button" disabled={isGenerating || isPreflighting} onClick={() => { ++referenceSequence.current; setCharacterReference(null); }} className="min-h-10 rounded-lg border px-2">Remove reference</button>
                      </div>}
                      <label className="mt-2 flex items-center gap-2 text-xs font-bold text-[#151515]">
                        <input type="checkbox" checked={useCustomPromptOnly || usePhotographicFinish}
                          disabled={isGenerating || isPreflighting || usePhotographicFinish || !customPrompt.trim()}
                          onChange={event => { setUseCustomPromptOnly(event.target.checked); setPreflight(null); setPrepared(null); }}
                          className="accent-[#96ba10]" />
                        Use only my prompt
                      </label>
                      <p className="mt-1 text-[10px] text-[#151515]/60">Uses your text with reference-role instructions when references are enabled. Design details may change.</p>
                    </div>
                  )}
                </div>

                </div>
              </details>

              <div className="rounded-2xl border-2 border-[#151515] bg-white p-3 shadow-[3px_3px_0_0_#151515]">
                <div className="flex items-start gap-2">
                  <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${hasValidPreflight ? 'bg-[#c9ff3d]' : 'bg-[#eee8dc]'}`}>
                    {hasValidPreflight ? <Check size={14} strokeWidth={3} /> : <span className="text-[10px] font-black">2</span>}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-black uppercase">Preview · free</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-[#151515]/50">Preview your camera journey and check that this scene can be rendered. No credits are used.</p>
                  </div>
                </div>
                <button type="button" onClick={() => void (videoGenerationEnabled ? runPreflight() : previewLocally())}
                  disabled={isCapturing || isPreparingControls || isPreflighting || isGenerating || referenceLoading || isPreparingGuide || !sourceFrame || routePoints.length < 2}
                  className="mt-3 min-h-11 w-full rounded-xl border-2 border-[#c9ff3d] bg-[#c9ff3d] px-4 py-2 text-sm font-bold text-slate-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white disabled:opacity-40">
                  {isPreparingControls || isPreflighting ? 'Preparing preview…' : 'Preview · free'}
                </button>
                {(isPreparingControls||isPreflighting) && <button type="button" onClick={()=>void cancelFreePreview()} disabled={isCancelling}
                  className="mt-2 min-h-11 w-full rounded-xl border border-[#151515] px-3 text-sm font-bold disabled:opacity-40">
                  {isCancelling?'Cancelling…':'Cancel preview'}
                </button>}
                <p className="mt-1 text-center text-xs text-[#151515]/70">Review the camera journey before the paid step.</p>
                {hasValidPreflight && preflight && (
                  <div className="mt-2 flex items-center gap-2 rounded-lg bg-[#edf8e7] px-2.5 py-2 text-[10px] font-bold text-[#285b22]">
                    <Check size={12} /> Ready · {preflight.width}×{preflight.height} · Omni 1.1
                  </div>
                )}
              </div>

              <div className="rounded-2xl border-2 border-[#151515] bg-[#151515] p-3 text-white shadow-[3px_3px_0_0_#ff6b57]">
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/10 text-[10px] font-black">3</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-black uppercase">{provider === 'internal_enhance' ? `Run ${internalEnhanceQuality === 'gpu_detail' ? 'GPU Detail' : 'Fast Cleanup'}` : `Generate with ${providerName(provider)}`}</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-white/50">Generate one finished video at the estimated cost below. There are no automatic paid retries.</p>
                  </div>
                </div>
                <button onClick={() => void generate()} disabled={!hasValidPreflight || isGenerating || isPreparingGuide || !providerCanRun} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border-2 border-white bg-gradient-to-r from-[#28c7e8] to-[#c9ff3d] px-3 py-2.5 text-xs font-black uppercase text-[#151515] transition hover:brightness-105 disabled:cursor-not-allowed disabled:grayscale disabled:opacity-40">
                  {isGenerating ? <Loader2 size={15} className="animate-spin" /> : <Film size={15} />}
                  {!videoGenerationEnabled ? 'Finished generation unavailable' : isGenerating
                    ? provider === 'internal_enhance' ? 'Restoring exact City Prompt frames…' : 'Rendering one continuous shot…'
                    : provider === 'internal_enhance'
                      ? `${internalEnhanceQuality === 'gpu_detail' ? 'Run GPU pass' : 'Run fast pass'} · unlimited local runs · est. $0.00`
                      : providerCanRun
                        ? `Generate video · est. $${(hasValidCost ? preflight!.estimated_cost_usd.toFixed(2) : '—')}${usePhotographicFinish && !prepared?.appearance_attempt_id && photographicGuide?.signature !== appearanceSignature ? ' + 26 tokens for photographic guide' : ''}`
                        : 'Video limit reached'}
                </button>
                {hasValidPreflight && preflight?.total_credit_cost !== undefined && <p className="mt-2 text-xs text-white/80">Up to {preflight.total_credit_cost} tokens: {preflight.video_credit_cost} video + up to {preflight.photographic_guide_credit_cost} for a new photographic guide.</p>}
                {provider === 'omni' && controlMode === 'preview_video' && <p className="mt-2 text-[10px] text-white/60">Output estimate allows 10 seconds at the published 720p rate; input charges are extra. This is not a billing cap. Actual duration and dimensions are checked after generation.</p>}
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
                            Image similarity {Math.round(selectedAttempt.fidelity_score)}/100
                          </span>
                        )}
                      </div>
                      <p className="text-[9px] text-[#151515]/45">
                        {selectedAttempt.output_media?.duration_seconds ?? selectedAttempt.duration_seconds} sec · {selectedAttempt.output_media ? `${selectedAttempt.output_media.width}×${selectedAttempt.output_media.height} output` : selectedAttempt.mode === 'saved_render_animation' ? 'Finished render source' : selectedAttempt.render_quality === 'high' ? '1080p HQ source' : '720p source'} · {providerOrigin(selectedAttempt.provider)} · saved to project
                        {selectedAttempt.scene_revision_sha256
                          ? ` · scene ${selectedAttempt.scene_revision_sha256.slice(0, 10)}`
                          : ''}
                      </p>
                      {selectedAttempt.media_warning && <p className="mt-1 text-[10px] font-semibold text-[#8d2c23]">{selectedAttempt.media_warning}</p>}
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
                    <div className="flex items-center gap-1.5 border-t border-[#151515]/10 bg-white px-3 py-2" aria-label="Image similarity samples" title="Image similarity can be dominated by unchanged surroundings. Check the buildings, parks and streets visually.">
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
                            <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-black ${fidelityTone(attempt.fidelity_status)}`} title={`Image similarity ${attempt.fidelity_score.toFixed(1)} of 100; not a verification of building identity`}>
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
