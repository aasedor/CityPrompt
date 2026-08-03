import {
  Check,
  Clapperboard,
  Download,
  Film,
  Loader2,
  MapPinned,
  RefreshCw,
  ShieldCheck,
  Sparkles,
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

const FRAME_WIDTH = 1280;
const FRAME_HEIGHT = 720;
const STYLES = [
  { id: 'golden_hour', name: 'Golden hour', detail: 'Warm hero film' },
  { id: 'crisp_daylight', name: 'Crisp daylight', detail: 'Clean + precise' },
  { id: 'after_rain', name: 'After rain', detail: 'Reflective + rich' },
  { id: 'blue_hour', name: 'Blue hour', detail: 'Lights + atmosphere' },
  { id: 'warm_overcast', name: 'Soft overcast', detail: 'Calm + natural' },
  { id: 'watercolour', name: 'Watercolour', detail: 'Painterly concept' },
  { id: 'pen-and-ink', name: 'Pen & Ink', detail: 'Drafted linework' },
  { id: 'charcoal', name: 'Charcoal', detail: 'Tonal sketch' },
  { id: 'clay-maquette', name: 'Clay', detail: 'Physical maquette' },
  { id: 'woodblock', name: 'Wood Block', detail: 'Graphic print' },
] as const;

const MOTIONS = [
  { id: 'path_follow', name: 'Path follow' },
  { id: 'forward_descent', name: 'Forward + descend' },
  { id: 'reveal_ascent', name: 'Reveal + rise' },
  { id: 'orbit_left', name: 'Orbit left' },
  { id: 'orbit_right', name: 'Orbit right' },
  { id: 'street_walkby', name: 'Street walk-by' },
] as const;

type StyleId = typeof STYLES[number]['id'];
type MotionId = typeof MOTIONS[number]['id'];

export interface VideoAttempt {
  id: string;
  request_id: string;
  status: string;
  style: string;
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
  route_points: VideoRoutePoint[];
  style: StyleId;
  camera_motion: MotionId;
  duration_seconds: 8;
  scene_brief: string;
  reference_images_base64: string[];
}

interface VideoGeneratePanelProps {
  projectId: string;
  canvas: HTMLCanvasElement | null;
  siteZones: SiteZone[];
  waitForTilesSettled?: () => Promise<boolean>;
  onBeforeCapture?: () => Promise<void>;
  captureAerialFrame?: () => Promise<string | null>;
  captureStreetFrame?: () => Promise<string | null>;
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
  onVideoSaved,
  onClose,
}: VideoGeneratePanelProps) {
  const [sourceFrame, setSourceFrame] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(true);
  const [routePoints, setRoutePoints] = useState<VideoRoutePoint[]>(DEFAULT_VIDEO_ROUTE);
  const [drawingRoute, setDrawingRoute] = useState(false);
  const [style, setStyle] = useState<StyleId>('golden_hour');
  const [motion, setMotion] = useState<MotionId>('path_follow');
  const [pilot, setPilot] = useState<VideoPilotState>({ attempts: [], attempts_used: 0, attempts_remaining: 40, max_attempts: 40 });
  const [preflight, setPreflight] = useState<PreflightResult | null>(null);
  const [prepared, setPrepared] = useState<PreparedVideoRequest | null>(null);
  const [isPreflighting, setIsPreflighting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAttempt, setSelectedAttempt] = useState<VideoAttempt | null>(null);
  const captureStarted = useRef(false);
  const captureSequence = useRef(0);
  const sceneContract = useMemo(() => buildVideoSceneContract(siteZones), [siteZones]);

  const currentSignature = useMemo(
    () => `${style}:${motion}:${routeSignature(routePoints)}:${sceneContract.signature}`,
    [motion, routePoints, sceneContract.signature, style],
  );
  const preparedSignature = prepared
    ? `${prepared.style}:${prepared.camera_motion}:${routeSignature(prepared.route_points)}:${prepared.scene_brief.startsWith(sceneContract.text) ? sceneContract.signature : 'stale'}`
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
    // Pilot comparison showed that catalog stills can improve facade finish but
    // also compete with the authored first-frame massing and elongate roof voids.
    // Video therefore defaults to geometry-first image-to-video: the exact 3D
    // capture defines all geometry and the catalog-derived text defines finish.
    const sceneBrief = `${sceneContract.text}\nREFERENCE POLICY: use the first frame as the only geometric and visual composition source. Archetype catalog data is textual appearance guidance only; do not substitute geometry from any other image.`;
    return {
      project_id: projectId,
      // Keep the literal first frame clean. Route geometry travels as structured
      // coordinates + prompt text; burning it into the image makes video models
      // preserve the markup as though it were part of the authored site.
      guide_frame_base64: sourceFrame,
      route_points: routePoints,
      style,
      camera_motion: motion,
      duration_seconds: 8,
      scene_brief: sceneBrief,
      reference_images_base64: [],
    };
  }, [motion, projectId, routePoints, sceneContract, sourceFrame, style]);

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

  return (
    <div className="absolute inset-0 z-[70] flex items-center justify-center bg-[#081011]/88 p-3 backdrop-blur-md sm:p-6">
      <div className="flex max-h-[calc(100dvh-1.5rem)] w-full max-w-[1180px] flex-col overflow-hidden rounded-[28px] border-2 border-[#151515] bg-[#f7f2e8] shadow-[10px_10px_0_0_#151515] sm:max-h-[calc(100dvh-3rem)]">
        <header className="flex items-center gap-3 border-b-2 border-[#151515] bg-[#151515] px-4 py-3 text-white sm:px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#28c7e8] to-[#c9ff3d] text-[#151515]">
            <Clapperboard size={18} strokeWidth={2.5} />
          </div>
          <div className="min-w-0">
            <h2 className="text-sm font-black uppercase tracking-[0.14em] sm:text-base">Video Render</h2>
            <p className="truncate text-[11px] text-white/55">Draw the flight. Lock the scene. Generate one continuous shot.</p>
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
              <button onClick={() => setRoutePoints(motion === 'street_walkby' ? DEFAULT_STREET_VIDEO_ROUTE : DEFAULT_VIDEO_ROUTE)} disabled={isGenerating} className="ml-auto inline-flex items-center gap-1 rounded-full border border-white/15 px-2.5 py-1 text-[10px] font-bold text-white/65 hover:bg-white/10">
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

            <div className="mt-4 grid min-h-0 gap-3 sm:grid-cols-[1fr_1fr]">
              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-white/45">Visual style</p>
                <div className="grid grid-cols-2 gap-1.5 xl:grid-cols-3">
                  {STYLES.map((item) => (
                    <button key={item.id} aria-pressed={style === item.id} onClick={() => setStyle(item.id)} disabled={isGenerating} className={`rounded-xl border px-2.5 py-2 text-left transition ${style === item.id ? 'border-[#c9ff3d] bg-[#c9ff3d]/15 text-white' : 'border-white/10 bg-white/[0.04] text-white/55 hover:bg-white/[0.08]'}`}>
                      <span className="block text-[11px] font-bold">{item.name}</span>
                      <span className="block text-[9px] opacity-55">{item.detail}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-2 text-[10px] font-black uppercase tracking-[0.14em] text-white/45">Camera behavior</p>
                <div className="grid grid-cols-2 gap-1.5 xl:grid-cols-3">
                  {MOTIONS.map((item) => (
                    <button key={item.id} aria-pressed={motion === item.id} onClick={() => selectMotion(item.id)} disabled={isGenerating || isCapturing} className={`rounded-xl border px-2.5 py-2 text-left text-[11px] font-bold transition ${motion === item.id ? 'border-[#28c7e8] bg-[#28c7e8]/15 text-white' : 'border-white/10 bg-white/[0.04] text-white/55 hover:bg-white/[0.08]'}`}>
                      {item.name}
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
                    The captured pixels lock authored massing, roofs, courtyards, facade rhythm, materials, and open-space program; only storey count and height are repeated in text. Source-tile cars and pedestrians are removed, and pilot streets stay empty for more stable continuity.
                  </p>
                  <p className="mt-1 text-[10px] font-bold leading-relaxed text-[#151515]/55">
                    Geometry-first mode anchors to the captured model. Place names and archetype style descriptions are withheld from Omni; only the visual style selected above is applied to the full frame.
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
                    <p className="mt-0.5 text-[10px] leading-relaxed text-[#151515]/50">Checks the frame, route, quota, auth, and final prompt. Gemini is not called.</p>
                  </div>
                </div>
                <button onClick={() => void runPreflight()} disabled={isCapturing || isPreflighting || isGenerating || !sourceFrame || routePoints.length < 2 || pilot.attempts_remaining <= 0} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-[#f7f2e8] px-3 py-2 text-xs font-black uppercase transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40">
                  {isPreflighting ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
                  {isPreflighting ? 'Checking…' : hasValidPreflight ? 'Run check again' : 'Run free check'}
                </button>
                {hasValidPreflight && preflight && (
                  <div className="mt-2 flex items-center gap-2 rounded-lg bg-[#edf8e7] px-2.5 py-2 text-[10px] font-bold text-[#285b22]">
                    <Check size={12} /> Ready · {preflight.width}×{preflight.height} · {preflight.reference_image_count} archetype refs · {preflight.model}
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
                  {isGenerating ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
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
                      <p className="truncate text-[11px] font-black uppercase">{selectedAttempt.style.split(/[_-]/).join(' ')} · {selectedAttempt.camera_motion.split('_').join(' ')}</p>
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
                          <span className="min-w-0 flex-1 truncate text-[10px] font-bold capitalize">{attempt.style.split('_').join(' ')} · {attempt.camera_motion.split('_').join(' ')}</span>
                          <span className="text-[9px] font-black uppercase text-[#151515]/40">{attempt.status}</span>
                        </button>
                        {attempt.video_url && (
                          <a href={downloadUrl(attempt) ?? undefined} download className="rounded-full p-2 hover:bg-[#f7f2e8]" aria-label={`Download ${attempt.style.split('_').join(' ')} video`} title="Download MP4">
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
    </div>
  );
}
