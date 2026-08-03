import {
  Check,
  Clapperboard,
  Download,
  Film,
  Loader2,
  MapPinned,
  RefreshCw,
  ShieldCheck,
  X,
} from 'lucide-react';
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from 'react';
import { createPortal } from 'react-dom';
import toast from 'react-hot-toast';

import { getApiErrorMessage, resolveApiFileUrl, videoRenderApi } from '@/services/api';
import type { SiteZone } from '@/types';
import {
  appendRoutePoint,
  DEFAULT_STREET_VIDEO_ROUTE,
  DEFAULT_VIDEO_ROUTE,
  normalizedRoutePoint,
  resampleRoute,
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

const FRAME_WIDTH = 1280;
const FRAME_HEIGHT = 720;

const MOTIONS = [
  { id: 'path_follow', name: 'Aerial fly-through', detail: 'Slow + high oblique' },
  { id: 'street_walkby', name: 'Street walk-by', detail: 'Slow + pedestrian height' },
] as const;

const CONTROL_MODES: Array<{ id: VideoControlMode; name: string; detail: string }> = [
  { id: 'preview_video', name: 'Preview-video edit', detail: 'Recommended · exact 8-second camera' },
  { id: 'multi_keyframe', name: 'Route keyframes', detail: 'Experimental · 6 exact City Prompt views' },
  { id: 'single_frame', name: 'Single frame', detail: 'Original baseline method' },
];

type MotionId = typeof MOTIONS[number]['id'];

export interface VideoAttempt {
  id: string;
  request_id: string;
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
}

function videoAttemptLabel(attempt: VideoAttempt): string {
  const motion = attempt.camera_motion.split('_').join(' ');
  const control = attempt.control_mode === 'multi_keyframe'
    ? 'Route keyframes'
    : attempt.control_mode === 'preview_video'
      ? 'Preview-video edit'
      : 'Single frame';
  if (attempt.style === 'source_fidelity') return `${control} · ${motion}`;
  return `${attempt.style.split(/[_-]/).join(' ')} · ${motion}`;
}

interface VideoPilotState {
  attempts: VideoAttempt[];
  attempts_used: number;
  attempts_remaining: number;
  max_attempts: number;
}

interface PreflightResult {
  ready: boolean;
  provider_called: false;
  width: number;
  height: number;
  mime_type: string;
  prompt_preview: string;
  attempts_used: number;
  attempts_remaining: number;
  estimated_cost_usd: number;
  model: string;
  reference_image_count: number;
}

interface PreparedVideoRequest {
  project_id: string;
  guide_frame_base64: string;
  control_mode: VideoControlMode;
  route_keyframes_base64: string[];
  preview_video_base64?: string;
  preview_video_mime_type?: string;
  route_points: VideoRoutePoint[];
  camera_motion: MotionId;
  duration_seconds: 8;
  scene_brief: string;
}

interface VideoGeneratePanelProps {
  projectId: string;
  canvas: HTMLCanvasElement | null;
  siteZones: SiteZone[];
  waitForTilesSettled?: () => Promise<boolean>;
  onBeforeCapture?: () => Promise<void>;
  captureAerialFrame?: () => Promise<string | null>;
  captureStreetFrame?: () => Promise<string | null>;
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

async function normalizeImageFrame(source: string): Promise<string> {
  const image = await loadImage(source);
  const output = document.createElement('canvas');
  output.width = FRAME_WIDTH;
  output.height = FRAME_HEIGHT;
  const context = output.getContext('2d');
  if (!context) throw new Error('This browser cannot prepare a video frame.');

  const sourceAspect = image.naturalWidth / image.naturalHeight;
  const targetAspect = FRAME_WIDTH / FRAME_HEIGHT;
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
  context.drawImage(image, sx, sy, sw, sh, 0, 0, FRAME_WIDTH, FRAME_HEIGHT);
  return output.toDataURL('image/jpeg', 0.94);
}

async function captureSceneFrame(canvas: HTMLCanvasElement): Promise<string> {
  await new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
  const output = document.createElement('canvas');
  output.width = FRAME_WIDTH;
  output.height = FRAME_HEIGHT;
  const context = output.getContext('2d');
  if (!context) throw new Error('This browser cannot prepare a video frame.');

  const sourceWidth = canvas.width;
  const sourceHeight = canvas.height;
  if (sourceWidth < 640 || sourceHeight < 640) {
    throw new Error('Keep the globe visible at a larger size before opening Video Render.');
  }
  const sourceAspect = sourceWidth / sourceHeight;
  const targetAspect = FRAME_WIDTH / FRAME_HEIGHT;
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
  context.drawImage(canvas, sx, sy, sw, sh, 0, 0, FRAME_WIDTH, FRAME_HEIGHT);
  return output.toDataURL('image/jpeg', 0.94);
}

export function VideoGeneratePanel({
  projectId,
  canvas,
  siteZones,
  waitForTilesSettled,
  onBeforeCapture,
  captureAerialFrame,
  captureStreetFrame,
  captureRouteControls,
  onVideoSaved,
  onClose,
}: VideoGeneratePanelProps) {
  const [sourceFrame, setSourceFrame] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(true);
  const [routePoints, setRoutePoints] = useState<VideoRoutePoint[]>(DEFAULT_VIDEO_ROUTE);
  const [drawingRoute, setDrawingRoute] = useState(false);
  const [motion, setMotion] = useState<MotionId>('path_follow');
  const [controlMode, setControlMode] = useState<VideoControlMode>('preview_video');
  const [routeControls, setRouteControls] = useState<(VideoRouteCaptureResult & { signature: string }) | null>(null);
  const [isPreparingControls, setIsPreparingControls] = useState(false);
  const [pilot, setPilot] = useState<VideoPilotState>({ attempts: [], attempts_used: 0, attempts_remaining: 46, max_attempts: 46 });
  const [preflight, setPreflight] = useState<PreflightResult | null>(null);
  const [prepared, setPrepared] = useState<PreparedVideoRequest | null>(null);
  const [isPreflighting, setIsPreflighting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAttempt, setSelectedAttempt] = useState<VideoAttempt | null>(null);
  const captureStarted = useRef(false);
  const captureSequence = useRef(0);
  const sceneContract = useMemo(() => buildVideoSceneContract(siteZones), [siteZones]);
  const routeCaptureSignature = useMemo(
    () => `${motion}:${routeSignature(routePoints)}`,
    [motion, routePoints],
  );

  const currentSignature = useMemo(
    () => `${controlMode}:${motion}:${routeSignature(routePoints)}:${sceneContract.signature}`,
    [controlMode, motion, routePoints, sceneContract.signature],
  );
  const preparedSignature = prepared
    ? `${prepared.control_mode}:${prepared.camera_motion}:${routeSignature(prepared.route_points)}:${prepared.scene_brief.startsWith(sceneContract.text) ? sceneContract.signature : 'stale'}`
    : null;
  const hasValidPreflight = Boolean(preflight?.ready && preparedSignature === currentSignature);

  const loadPilot = useCallback(async () => {
    try {
      const state = await videoRenderApi.list(projectId) as VideoPilotState;
      setPilot(state);
      setSelectedAttempt((current) => current ?? state.attempts.find((attempt) => attempt.status === 'complete') ?? null);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError, 'Could not load Video Render history.'));
    }
  }, [projectId]);

  const capture = useCallback(async () => {
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
        ? await normalizeImageFrame(directCapture.startsWith('data:') ? directCapture : `data:image/png;base64,${directCapture}`)
        : await captureSceneFrame(canvas!);
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
  }, [canvas, captureAerialFrame, onBeforeCapture, waitForTilesSettled]);

  const captureStreet = useCallback(async () => {
    const sequence = ++captureSequence.current;
    if (!captureStreetFrame) {
      if (sequence === captureSequence.current) setError('Street walk-by capture is unavailable in this view.');
      return;
    }
    setIsCapturing(true);
    setError(null);
    try {
      const captured = await captureStreetFrame();
      if (!captured) throw new Error('Place the Street View marker beside the site, aim it along the frontage, then select Street walk-by again.');
      const source = captured.startsWith('data:') ? captured : `data:image/jpeg;base64,${captured}`;
      const normalized = await normalizeImageFrame(source);
      if (sequence === captureSequence.current) {
        setSourceFrame(normalized);
        setRouteControls(null);
        setPreflight(null);
        setPrepared(null);
      }
    } catch (captureError) {
      if (sequence === captureSequence.current) {
        setError(getApiErrorMessage(captureError, 'The street-level scene could not be captured.'));
      }
    } finally {
      if (sequence === captureSequence.current) setIsCapturing(false);
    }
  }, [captureStreetFrame]);

  const selectMotion = useCallback((nextMotion: MotionId) => {
    const wasStreet = motion === 'street_walkby';
    setMotion(nextMotion);
    setRouteControls(null);
    setRoutePoints(nextMotion === 'street_walkby' ? DEFAULT_STREET_VIDEO_ROUTE : DEFAULT_VIDEO_ROUTE);
    if (nextMotion === 'street_walkby') void captureStreet();
    else if (wasStreet) void capture();
  }, [capture, captureStreet, motion]);

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
    let activeControls = routeControls?.signature === routeCaptureSignature ? routeControls : null;
    if (controlMode !== 'single_frame' && !activeControls) {
      if (!captureRouteControls) throw new Error('This 3D view cannot prepare route controls yet.');
      setIsPreparingControls(true);
      try {
        const captured = await captureRouteControls({
          routePoints,
          cameraMotion: motion,
          durationSeconds: 8,
          keyframeCount: 6,
        });
        const normalizedKeyframes = await Promise.all(captured.keyframesBase64.map((frame) => (
          normalizeImageFrame(frame.startsWith('data:') ? frame : `data:image/png;base64,${frame}`)
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

    const sceneBrief = controlMode === 'multi_keyframe'
      ? `${sceneContract.text}\nSOURCE POLICY: The ordered City Prompt route images are the only visual authorities. They depict one unchanged scene along the exact desired path. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`
      : controlMode === 'preview_video'
        ? `${sceneContract.text}\nSOURCE POLICY: The City Prompt route preview is the exact camera and geometry authority. Preserve every frame's layout and timing. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`
        : `${sceneContract.text}\nSOURCE POLICY: Image1 is the only visual input. Animate the captured scene as-is. Do not restyle, relight, beautify, materialize, reinterpret, or add detail.`;
    const routeKeyframes = controlMode === 'multi_keyframe' ? activeControls?.keyframesBase64 ?? [] : [];
    return {
      project_id: projectId,
      guide_frame_base64: routeKeyframes[0] ?? sourceFrame,
      control_mode: controlMode,
      route_keyframes_base64: routeKeyframes,
      ...(controlMode === 'preview_video' && activeControls ? {
        preview_video_base64: activeControls.previewVideoBase64,
        preview_video_mime_type: activeControls.previewVideoMimeType,
      } : {}),
      route_points: routePoints,
      camera_motion: motion,
      duration_seconds: 8,
      scene_brief: sceneBrief,
    };
  }, [captureRouteControls, controlMode, motion, projectId, routeCaptureSignature, routeControls, routePoints, sceneContract, sourceFrame]);

  const runPreflight = useCallback(async () => {
    setIsPreflighting(true);
    setError(null);
    try {
      const body = await requestBody();
      const result = await videoRenderApi.preflight(body) as PreflightResult;
      setPrepared(body);
      setPreflight(result);
      setPilot((current) => ({ ...current, attempts_used: result.attempts_used, attempts_remaining: result.attempts_remaining }));
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
    if (!prepared || !hasValidPreflight || pilot.attempts_remaining <= 0) return;
    setIsGenerating(true);
    setError(null);
    try {
      const result = await videoRenderApi.generate({
        ...prepared,
        request_id: crypto.randomUUID(),
        confirm_paid_submission: true,
      }) as { attempt: VideoAttempt; attempts_used: number; attempts_remaining: number };
      setSelectedAttempt(result.attempt);
      setPreflight(null);
      setPrepared(null);
      onVideoSaved?.(result.attempt);
      await loadPilot();
      toast.success(`Video trial ${result.attempts_used} is ready`);
    } catch (generationError) {
      setError(getApiErrorMessage(generationError, 'The Omni video submission failed.'));
      await loadPilot();
    } finally {
      setIsGenerating(false);
    }
  }, [hasValidPreflight, loadPilot, onVideoSaved, pilot.attempts_remaining, prepared]);

  const beginRoute = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (isGenerating) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrawingRoute(true);
    setRouteControls(null);
    setRoutePoints([normalizedRoutePoint(event.clientX, event.clientY, event.currentTarget.getBoundingClientRect())]);
  };
  const continueRoute = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!drawingRoute) return;
    const point = normalizedRoutePoint(event.clientX, event.clientY, event.currentTarget.getBoundingClientRect());
    setRoutePoints((current) => appendRoutePoint(current, point));
  };
  const finishRoute = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!drawingRoute) return;
    event.currentTarget.releasePointerCapture(event.pointerId);
    setDrawingRoute(false);
    setRoutePoints((current) => resampleRoute(current));
  };

  const activeVideoUrl = selectedAttempt?.video_url ? resolveApiFileUrl(selectedAttempt.video_url) : null;
  const downloadUrl = useCallback((attempt: VideoAttempt) => {
    if (!attempt.video_url) return null;
    const fileName = `city-prompt-${attempt.style}-${attempt.camera_motion}-${attempt.id.slice(0, 8)}.mp4`;
    const separator = attempt.video_url.includes('?') ? '&' : '?';
    return `${resolveApiFileUrl(attempt.video_url)}${separator}download=true&filename=${encodeURIComponent(fileName)}`;
  }, []);
  const usedDots = Array.from({ length: pilot.max_attempts }, (_, index) => index < pilot.attempts_used);

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
            <span className="text-[10px] font-bold uppercase tracking-wider text-white/50">Pilot calls</span>
            <div className="flex gap-1">
              {usedDots.map((used, index) => (
                <span key={index} className={`h-2 w-2 rounded-full ${used ? 'bg-[#ff6b57]' : 'bg-white/20'}`} />
              ))}
            </div>
            <span className="text-xs font-black">{pilot.attempts_used}/{pilot.max_attempts}</span>
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
              <span className="text-[11px] text-white/45">Drag from start to finish · the red guide is removed from the video</span>
              <button onClick={() => {
                setRouteControls(null);
                setRoutePoints(motion === 'street_walkby' ? DEFAULT_STREET_VIDEO_ROUTE : DEFAULT_VIDEO_ROUTE);
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
                  Preparing six geographic route views and the exact 8-second camera preview…
                  <span className="mt-1 text-[10px] font-normal text-white/45">No Omni call or credit is used during this step.</span>
                </div>
              )}
              {!isCapturing && !sourceFrame && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 px-8 text-center text-sm text-white/60">
                  <Film size={28} />
                  <span>The scene could not be captured.</span>
                  <button onClick={() => void (motion === 'street_walkby' ? captureStreet() : capture())} className="rounded-full bg-white px-4 py-2 text-xs font-black uppercase text-[#151515]">Try capture again</button>
                </div>
              )}
              {sourceFrame && (
                <div
                  className={`absolute inset-0 touch-none ${drawingRoute ? 'cursor-crosshair' : 'cursor-cell'}`}
                  onPointerDown={beginRoute}
                  onPointerMove={continueRoute}
                  onPointerUp={finishRoute}
                  onPointerCancel={finishRoute}
                  aria-label={motion === 'street_walkby' ? 'Draw pedestrian walk-by path' : 'Draw drone flight path'}
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
                      <circle key={`${point.x}-${point.y}-${index}`} cx={point.x * 100} cy={point.y * 100} r={index === 0 ? 1.5 : 0.8} fill={index === 0 ? 'white' : '#ff3b4f'} stroke="#ff3b4f" strokeWidth="0.7" vectorEffect="non-scaling-stroke" />
                    ))}
                  </svg>
                </div>
              )}
              <div className="pointer-events-none absolute bottom-3 left-3 rounded-full bg-black/65 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-white/75 backdrop-blur">
                16:9 · 720p · 8 sec · one shot
              </div>
            </div>

            {routeControls?.signature === routeCaptureSignature && controlMode !== 'single_frame' && (
              <div className="mt-3 rounded-xl border border-white/10 bg-black/25 p-2">
                <div className="mb-2 flex items-center justify-between text-[9px] font-black uppercase tracking-wider text-white/45">
                  <span>{controlMode === 'multi_keyframe' ? 'Ordered route checkpoints' : 'Deterministic camera preview'}</span>
                  <span className="text-[#c9ff3d]">Prepared locally</span>
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
              </div>
            )}

            <div className="mt-4 grid min-h-0 gap-3 sm:grid-cols-[1.15fr_0.85fr]">
              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-white/45">Motion control</p>
                <div className="grid grid-cols-3 gap-1.5">
                  {CONTROL_MODES.map((item) => (
                    <button key={item.id} aria-pressed={controlMode === item.id} onClick={() => {
                      setControlMode(item.id);
                      setPreflight(null);
                      setPrepared(null);
                    }} disabled={isGenerating || isCapturing || isPreparingControls} className={`rounded-xl border px-2 py-2 text-left transition ${controlMode === item.id ? 'border-[#c9ff3d] bg-[#c9ff3d]/15 text-white' : 'border-white/10 bg-white/[0.04] text-white/55 hover:bg-white/[0.08]'}`}>
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
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Scene lock</p>
                  <span className="inline-flex items-center gap-1 rounded-full bg-[#fff0bf] px-2 py-1 text-[9px] font-black uppercase text-[#705000]"><ShieldCheck size={11} /> Continuity constrained</span>
                </div>
                <div className="rounded-xl border border-[#151515]/15 bg-white/65 p-3">
                  <p className="text-xs font-black leading-relaxed text-[#151515]/80">{sceneContract.summary}</p>
                  <p className="mt-1 text-[10px] font-semibold leading-relaxed text-[#151515]/55">
                    The captured pixels lock authored massing, roofs, courtyards, facade rhythm, materials, lighting, context buildings, and open-space program. Source-tile cars and pedestrians are removed, and streets stay empty for more stable continuity.
                  </p>
                  <p className="mt-1 text-[10px] font-bold leading-relaxed text-[#151515]/55">
                    {controlMode === 'multi_keyframe'
                      ? 'Omni receives six ordered City Prompt views of the same scene, with no style or archetype reference images.'
                      : controlMode === 'preview_video'
                        ? 'Omni edits City Prompt’s deterministic route video, which carries the exact camera timing and scene geometry.'
                        : 'Omni receives one authoritative image plus conservative camera-motion instructions.'}
                  </p>
                  <p className="mt-2 rounded-lg bg-[#fff0bf] px-2 py-1.5 text-[9px] font-bold leading-relaxed text-[#705000]">
                    AI concept visualization: Omni can still reinterpret geometry between frames. Verify the video against the 3D scene before using it for design decisions.
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
                    <p className="mt-0.5 text-[10px] leading-relaxed text-[#151515]/50">Prepares route controls, then checks every input, quota, auth, and final prompt. Gemini is not called.</p>
                  </div>
                </div>
                <button onClick={() => void runPreflight()} disabled={isCapturing || isPreparingControls || isPreflighting || isGenerating || !sourceFrame || routePoints.length < 2 || pilot.attempts_remaining <= 0} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-[#f7f2e8] px-3 py-2 text-xs font-black uppercase transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40">
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
                    <p className="text-xs font-black uppercase">Generate with Omni</p>
                    <p className="mt-0.5 text-[10px] leading-relaxed text-white/50">One click = one paid provider call. There are no automatic retries.</p>
                  </div>
                </div>
                <button onClick={() => void generate()} disabled={!hasValidPreflight || isGenerating || pilot.attempts_remaining <= 0} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border-2 border-white bg-gradient-to-r from-[#28c7e8] to-[#c9ff3d] px-3 py-2.5 text-xs font-black uppercase text-[#151515] transition hover:brightness-105 disabled:cursor-not-allowed disabled:grayscale disabled:opacity-40">
                  {isGenerating ? <Loader2 size={15} className="animate-spin" /> : <Film size={15} />}
                  {isGenerating ? 'Rendering one continuous shot…' : pilot.attempts_remaining > 0 ? `Generate trial ${pilot.attempts_used + 1} of ${pilot.max_attempts} · est. $0.80` : `${pilot.max_attempts}-trial cap reached`}
                </button>
                {isGenerating && <p className="mt-2 text-center text-[10px] text-white/45">Keep this panel open. High-quality video can take several minutes.</p>}
              </div>

              {error && <div role="alert" className="rounded-xl border border-[#c94739]/30 bg-[#ffe5df] px-3 py-2.5 text-[11px] font-semibold leading-relaxed text-[#8d2c23]">{error}</div>}

              {activeVideoUrl && selectedAttempt && (
                <div className="overflow-hidden rounded-2xl border-2 border-[#151515] bg-black shadow-[3px_3px_0_0_#151515]">
                  <video key={activeVideoUrl} controls playsInline autoPlay muted loop className="aspect-video w-full bg-black" src={activeVideoUrl} />
                  <div className="flex items-center gap-2 bg-white px-3 py-2">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-[11px] font-black uppercase">{videoAttemptLabel(selectedAttempt)}</p>
                      <p className="text-[9px] text-[#151515]/45">8 sec · Gemini Omni · saved to project</p>
                    </div>
                    <a href={downloadUrl(selectedAttempt) ?? activeVideoUrl} download className="inline-flex items-center gap-1.5 rounded-full border-2 border-[#151515] px-3 py-2 text-[10px] font-black uppercase hover:bg-[#f7f2e8]" aria-label="Download video"><Download size={14} /> MP4</a>
                  </div>
                </div>
              )}

              {pilot.attempts.length > 0 && (
                <div>
                  <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-[#151515]/45">Pilot history</p>
                  <div className="space-y-1.5">
                    {pilot.attempts.map((attempt, index) => (
                      <div key={attempt.id} className={`flex w-full items-center gap-1 rounded-xl border px-1.5 py-1 ${selectedAttempt?.id === attempt.id ? 'border-[#151515] bg-white' : 'border-[#151515]/10 bg-white/45'}`}>
                        <button onClick={() => attempt.video_url && setSelectedAttempt(attempt)} className={`flex min-w-0 flex-1 items-center gap-2 rounded-lg px-1 py-1 text-left ${attempt.video_url ? 'hover:bg-[#f7f2e8]' : 'cursor-default'}`}>
                          <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-black ${attempt.status === 'complete' ? 'bg-[#c9ff3d]' : attempt.status === 'failed' ? 'bg-[#ffb5a9]' : 'bg-[#eee8dc]'}`}>{pilot.attempts_used - index}</span>
                          <span className="min-w-0 flex-1 truncate text-[10px] font-bold capitalize">{videoAttemptLabel(attempt)}</span>
                          <span className="text-[9px] font-black uppercase text-[#151515]/40">{attempt.status}</span>
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
