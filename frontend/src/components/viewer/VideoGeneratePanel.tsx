/**
 * VideoGeneratePanel — UI for generating flythrough videos from aerial renders.
 *
 * Takes an existing render as the first frame, lets the user pick camera motion
 * and duration, then calls the Veo 3.1 Fast backend to generate an 8-second
 * cinematic flythrough video. Polls for completion and shows inline playback.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuthStore } from '@/store';
import { authApi } from '@/services/api';

const API_BASE = import.meta.env.VITE_API_URL || '';
const VIDEO_API_URL = `${API_BASE}/api/v1/video`;
const VIDEO_TOKEN_COST = 50;
const POLL_INTERVAL_MS = 10_000;

// ---------------------------------------------------------------------------
// Camera motion presets
// ---------------------------------------------------------------------------

const CAMERA_MOTIONS = [
  { id: 'tracking_forward', label: 'Tracking Forward', icon: '\u2193', desc: 'Dolly in toward the site' },
  { id: 'tracking_backward', label: 'Tracking Backward', icon: '\u2191', desc: 'Pull back to reveal context' },
  { id: 'orbit_left', label: 'Orbit Left', icon: '\u21BA', desc: 'Rotate counter-clockwise' },
  { id: 'orbit_right', label: 'Orbit Right', icon: '\u21BB', desc: 'Rotate clockwise' },
  { id: 'crane_up', label: 'Crane Up', icon: '\u2197', desc: 'Rise upward, reveal surroundings' },
  { id: 'static_life', label: 'Static + Life', icon: '\u2733', desc: 'Fixed camera, animate scene' },
] as const;

type CameraMotionId = typeof CAMERA_MOTIONS[number]['id'];

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface VideoGeneratePanelProps {
  /** Base64 image data URI of the completed aerial render (first frame) */
  renderImageUrl: string;
  /** Optional: base64 of second frame for first/last frame conditioning */
  lastFrameImageUrl?: string;
  /** Called when video generation is complete */
  onVideoReady?: (videoDataUri: string) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function VideoGeneratePanel({ renderImageUrl, lastFrameImageUrl, onVideoReady }: VideoGeneratePanelProps) {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const isAdmin = user?.role === 'admin' || user?.role === 'cofounder';
  const credits = user?.render_credits ?? 0;
  const canAfford = isAdmin || credits >= VIDEO_TOKEN_COST;

  // Form state
  const [cameraMotion, setCameraMotion] = useState<CameraMotionId>('tracking_forward');
  const [duration, setDuration] = useState<4 | 8>(8);
  const [customPrompt, setCustomPrompt] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Generation state
  const [status, setStatus] = useState<'idle' | 'generating' | 'complete' | 'error'>('idle');
  const [, setOperationName] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [estimatedSeconds, setEstimatedSeconds] = useState(60);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [videoDataUri, setVideoDataUri] = useState<string | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Cleanup intervals on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const refreshCredits = useCallback(async () => {
    try { const u = await authApi.me(); setUser(u); } catch { /* ignore */ }
  }, [setUser]);

  // Extract base64 from data URI
  const extractBase64 = (dataUri: string): string => {
    const idx = dataUri.indexOf(',');
    return idx >= 0 ? dataUri.slice(idx + 1) : dataUri;
  };

  // ── Start generation ────────────────────────────────────────────────────

  const handleGenerate = useCallback(async () => {
    if (!canAfford) return;
    setStatus('generating');
    setErrorMessage(null);
    setVideoDataUri(null);
    setElapsed(0);

    const token = localStorage.getItem('access_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
      const body: Record<string, unknown> = {
        first_frame_base64: extractBase64(renderImageUrl),
        camera_motion: cameraMotion,
        duration_seconds: duration,
      };
      if (lastFrameImageUrl) {
        body.last_frame_base64 = extractBase64(lastFrameImageUrl);
      }
      if (customPrompt.trim()) {
        body.prompt = customPrompt.trim();
      }

      console.log(`[Video] Starting generation — motion: ${cameraMotion}, duration: ${duration}s`);

      const resp = await axios.post(`${VIDEO_API_URL}/generate`, body, {
        timeout: 30_000,
        headers,
      });

      const { operation_name, estimated_seconds } = resp.data;
      setOperationName(operation_name);
      setEstimatedSeconds(estimated_seconds || 60);

      console.log(`[Video] Operation started: ${operation_name}`);

      // Start elapsed timer
      timerRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);

      // Start polling
      pollRef.current = setInterval(async () => {
        try {
          console.log(`[Video] Polling ${operation_name}...`);
          const statusResp = await axios.get(
            `${VIDEO_API_URL}/status/${encodeURIComponent(operation_name)}`,
            { timeout: 15_000, headers },
          );

          const { status: opStatus, video_base64, error: opError } = statusResp.data;

          if (opStatus === 'complete' && video_base64) {
            // Stop polling
            if (pollRef.current) clearInterval(pollRef.current);
            if (timerRef.current) clearInterval(timerRef.current);
            pollRef.current = null;
            timerRef.current = null;

            const uri = `data:video/mp4;base64,${video_base64}`;
            setVideoDataUri(uri);
            setStatus('complete');
            onVideoReady?.(uri);
            refreshCredits();

            console.log(`[Video] Complete! Video size: ${video_base64.length} chars`);
          } else if (opStatus === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current);
            if (timerRef.current) clearInterval(timerRef.current);
            pollRef.current = null;
            timerRef.current = null;

            setStatus('error');
            setErrorMessage(opError || 'Video generation failed.');
            console.error(`[Video] Failed: ${opError}`);
          }
          // else still processing, continue polling
        } catch (pollErr) {
          console.warn('[Video] Poll error:', pollErr);
        }
      }, POLL_INTERVAL_MS);

    } catch (err: unknown) {
      setStatus('error');
      const msg = err instanceof Error ? err.message : 'Failed to start video generation';
      setErrorMessage(msg);
      console.error('[Video] Start error:', err);
    }
  }, [canAfford, renderImageUrl, lastFrameImageUrl, cameraMotion, duration, customPrompt, onVideoReady, refreshCredits]);

  // ── Download video ──────────────────────────────────────────────────────

  const handleDownload = useCallback(() => {
    if (!videoDataUri) return;
    const a = document.createElement('a');
    a.href = videoDataUri;
    a.download = `flythrough-${cameraMotion}-${Date.now()}.mp4`;
    a.click();
  }, [videoDataUri, cameraMotion]);

  // ── Reset ───────────────────────────────────────────────────────────────

  const handleReset = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
    pollRef.current = null;
    timerRef.current = null;
    setStatus('idle');
    setOperationName(null);
    setElapsed(0);
    setErrorMessage(null);
    setVideoDataUri(null);
  }, []);

  // ── Progress percentage estimate ────────────────────────────────────────

  const progressPct = Math.min(95, Math.round((elapsed / estimatedSeconds) * 100));

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2">
        <svg className="h-4 w-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <span className="text-xs font-semibold text-white/90 uppercase tracking-wider">Flythrough Video</span>
        <span className="ml-auto text-[10px] text-white/40">Veo 3.1 Fast</span>
      </div>

      {/* ── Idle: show controls ─────────────────────────────────────────── */}
      {status === 'idle' && (
        <>
          {/* Camera motion selector */}
          <div>
            <label className="mb-1.5 block text-[10px] font-medium text-white/50 uppercase tracking-wider">
              Camera Motion
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {CAMERA_MOTIONS.map((motion) => (
                <button
                  key={motion.id}
                  onClick={() => setCameraMotion(motion.id)}
                  className={`flex items-center gap-1.5 rounded-md px-2.5 py-2 text-left text-[11px] font-medium transition ${
                    cameraMotion === motion.id
                      ? 'bg-purple-500/20 text-purple-300 ring-1 ring-purple-500/40'
                      : 'bg-white/[0.04] text-white/60 hover:bg-white/[0.08]'
                  }`}
                >
                  <span className="text-sm">{motion.icon}</span>
                  <span>{motion.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="mb-1.5 block text-[10px] font-medium text-white/50 uppercase tracking-wider">
              Duration
            </label>
            <div className="flex gap-2">
              {([4, 8] as const).map((d) => (
                <button
                  key={d}
                  onClick={() => setDuration(d)}
                  className={`flex-1 rounded-md py-1.5 text-xs font-medium transition ${
                    duration === d
                      ? 'bg-purple-500/20 text-purple-300 ring-1 ring-purple-500/40'
                      : 'bg-white/[0.04] text-white/60 hover:bg-white/[0.08]'
                  }`}
                >
                  {d}s
                </button>
              ))}
            </div>
          </div>

          {/* Advanced: custom prompt */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1 text-[10px] text-white/40 hover:text-white/60 transition"
          >
            <svg className={`h-3 w-3 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Advanced Options
          </button>
          {showAdvanced && (
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="Custom prompt override (optional)..."
              className="w-full rounded-md bg-white/[0.04] px-3 py-2 text-xs text-white/80 placeholder-white/30 ring-1 ring-white/10 focus:ring-purple-500/40 focus:outline-none resize-none"
              rows={3}
            />
          )}

          {/* Generate button */}
          <button
            onClick={handleGenerate}
            disabled={!canAfford}
            className={`w-full rounded-lg py-2.5 text-xs font-semibold transition ${
              canAfford
                ? 'bg-purple-600 text-white hover:bg-purple-500 shadow-lg shadow-purple-900/30'
                : 'bg-white/[0.06] text-white/30 cursor-not-allowed'
            }`}
          >
            {canAfford
              ? `Generate Flythrough (${VIDEO_TOKEN_COST} tokens)`
              : `Insufficient tokens (need ${VIDEO_TOKEN_COST})`
            }
          </button>
        </>
      )}

      {/* ── Generating: progress ────────────────────────────────────────── */}
      {status === 'generating' && (
        <div className="space-y-3">
          <div className="text-center">
            <div className="mb-2 text-xs text-white/60">Generating flythrough...</div>
            <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-1000"
                style={{ width: `${progressPct}%` }}
              />
            </div>
            <div className="mt-1.5 flex justify-between text-[10px] text-white/40">
              <span>{elapsed}s elapsed</span>
              <span>~{estimatedSeconds}s est.</span>
            </div>
          </div>
          <div className="rounded-md bg-white/[0.04] px-3 py-2 text-[10px] text-white/40 space-y-0.5">
            <div>Model: Veo 3.1 Fast</div>
            <div>Motion: {CAMERA_MOTIONS.find((m) => m.id === cameraMotion)?.label}</div>
            <div>Duration: {duration}s</div>
          </div>
          <button
            onClick={handleReset}
            className="w-full rounded-md py-1.5 text-[10px] font-medium text-white/40 ring-1 ring-white/10 hover:bg-white/[0.06] transition"
          >
            Cancel
          </button>
        </div>
      )}

      {/* ── Complete: video player ──────────────────────────────────────── */}
      {status === 'complete' && videoDataUri && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-green-400">Video ready</span>
            <div className="flex gap-1">
              <button
                onClick={handleDownload}
                className="rounded px-2 py-1 text-[10px] font-medium text-gray-300 transition hover:bg-white/10"
                title="Download MP4"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
              </button>
              <button
                onClick={handleReset}
                className="rounded px-2 py-1 text-[10px] font-medium text-gray-300 transition hover:bg-white/10"
                title="New video"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
                </svg>
              </button>
            </div>
          </div>
          <video
            src={videoDataUri}
            controls
            autoPlay
            loop
            className="w-full rounded-lg shadow-md"
          />
        </div>
      )}

      {/* ── Error ───────────────────────────────────────────────────────── */}
      {status === 'error' && (
        <div className="space-y-2">
          <div className="rounded-md bg-red-500/10 px-3 py-2 text-xs text-red-400 ring-1 ring-red-500/20">
            {errorMessage || 'Video generation failed.'}
          </div>
          <button
            onClick={handleReset}
            className="w-full rounded-md py-1.5 text-xs font-medium text-white/60 ring-1 ring-white/10 hover:bg-white/[0.06] transition"
          >
            Try Again
          </button>
        </div>
      )}

      {/* ── Token info ──────────────────────────────────────────────────── */}
      {status === 'idle' && !isAdmin && (
        <div className="text-[10px] text-white/30 text-center">
          Cost: {VIDEO_TOKEN_COST} tokens per video | Balance: {credits.toLocaleString()}
        </div>
      )}
    </div>
  );
}
