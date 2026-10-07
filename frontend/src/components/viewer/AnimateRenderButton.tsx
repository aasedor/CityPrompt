import { useCallback, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Download, Film, Loader2, RefreshCw, X } from 'lucide-react';
import { authApi, getApiErrorMessage, renderAnimationApi, resolveApiFileUrl, videoRenderApi } from '@/services/api';
import { useAuthStore } from '@/store';
import type { SavedRender } from '@/types';
import { savedRenderIsSource } from '@/utils/renderPresentation';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import type { VideoAttempt } from './VideoGeneratePanel';
import { LocalComfyTrialButton } from './LocalComfyTrialButton';

export interface AnimationPreflight {
  ready: true;
  provider_called: false;
  source_render_id: string;
  width: number;
  height: number;
  duration_seconds: 5;
  generate_audio: false;
  estimated_cost_usd: number;
  credit_cost: number;
  model: string;
  attempts_remaining: number;
}

interface Props {
  projectId: string;
  render: SavedRender;
  onSaved?: (attempt: VideoAttempt) => void;
  onImageSaved?: (render: SavedRender) => void;
}

/** Only a saved, finished image can be chosen; the request carries IDs, never
 * the displayed preview URL, a viewport capture or client-supplied pixels. */
export function AnimateRenderButton(props: Props) {
  return <><LocalComfyTrialButton {...props} /><KlingAnimateRenderButton {...props} /></>;
}

function KlingAnimateRenderButton(props: Props) {
  const [open, setOpen] = useState(false);
  const close = useCallback(() => setOpen(false), []);
  if (savedRenderIsSource(props.render)) return null;
  return <>
    <button type="button" onClick={() => setOpen(true)}
      className="inline-flex min-h-11 items-center gap-2 rounded-full bg-[#28c7e8] px-3 py-2 text-xs font-bold text-[#151515] shadow-lg ring-1 ring-white/20 hover:bg-cyan-200">
      <Film size={16} /> Animate this render
    </button>
    {open && createPortal(<AnimateRenderDialog key={`${props.projectId}:${props.render.id}`} {...props}
      onClose={close} />, document.body)}
  </>;
}

function AnimateRenderDialog({ projectId, render, onSaved, onClose }: Props & { onClose: () => void }) {
  const [preflight, setPreflight] = useState<AnimationPreflight | null>(null);
  const [attempt, setAttempt] = useState<VideoAttempt | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);
  const inFlight = useRef(false);
  const savedCallback = useRef(onSaved);
  const closeButton = useRef<HTMLButtonElement>(null);
  const pendingKey = `cityprompt.animation.v1:${projectId}:${render.id}`;
  const requestId = useRef(readBrowserPreference(pendingKey) || crypto.randomUUID());
  savedCallback.current = onSaved;

  const acceptAttempt = useCallback((value: VideoAttempt) => {
    if (!mounted.current) return;
    setAttempt(value);
    if (value.status === 'complete' && value.video_url) {
      writeBrowserPreference(pendingKey, null);
      savedCallback.current?.(value);
    }
  }, [pendingKey]);

  const loadHistory = useCallback(async () => {
    const state = await videoRenderApi.list(projectId) as { attempts: VideoAttempt[] };
    const existing = state.attempts.find(item => item.provider === 'kling' && item.mode === 'saved_render_animation' && item.source_render_id === render.id);
    if (existing) acceptAttempt(existing);
    return existing;
  }, [acceptAttempt, projectId, render.id]);

  useEffect(() => {
    mounted.current = true;
    const previousFocus = document.activeElement as HTMLElement | null;
    closeButton.current?.focus();
    const keydown = (event: KeyboardEvent) => {
      event.stopPropagation(); // Do not advance/close the underlying still lightbox.
      if (event.key === 'Escape') onClose();
      if (event.key === 'Tab') {
        const elements = closeButton.current?.closest('[role="dialog"]')?.querySelectorAll<HTMLElement>(
          'button:not(:disabled), a[href], video[controls]',
        );
        if (!elements?.length) return;
        const first = elements[0], last = elements[elements.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener('keydown', keydown, true);
    void Promise.allSettled([
      renderAnimationApi.preflight({ project_id: projectId, source_render_id: render.id }),
      loadHistory(),
    ]).then(([check, history]) => {
      if (!mounted.current) return;
      if (check.status === 'fulfilled') setPreflight(check.value);
      else setError(getApiErrorMessage(check.reason, 'Animation is currently unavailable.'));
      if (history.status === 'rejected') setError('Could not check existing animation jobs. Reopen this panel before generating.');
      setLoading(false);
    });
    return () => {
      mounted.current = false;
      document.removeEventListener('keydown', keydown, true);
      previousFocus?.focus();
    };
  }, [loadHistory, onClose, projectId, render.id]);

  const recover = useCallback(async (id: string) => {
    if (inFlight.current) return;
    inFlight.current = true;
    setChecking(true);
    try {
      const value = await renderAnimationApi.recover(projectId, id);
      if (mounted.current) { setError(null); acceptAttempt(value); }
    } catch (exc) {
      if (mounted.current) setError(getApiErrorMessage(exc, 'Could not check the saved request. Try again; no new generation will be submitted.'));
    } finally {
      inFlight.current = false;
      if (mounted.current) setChecking(false);
    }
  }, [acceptAttempt, projectId]);

  useEffect(() => {
    if (!attempt?.recoverable || error || attempt.error) return;
    const timer = window.setTimeout(() => void recover(attempt.id), 5000);
    return () => window.clearTimeout(timer);
  }, [attempt, error, recover]);

  // A receipt can arrive after another tab reopened the saved still. Reads here
  // find it without sending a second paid request, even if there is no ID yet.
  useEffect(() => {
    if (!attempt || !['reserved', 'submitting'].includes(attempt.status)) return;
    const timer = window.setTimeout(() => void loadHistory().catch(() => {
      if (mounted.current) setError('Could not refresh the saved job. Reopen this panel to recover it.');
    }), 5000);
    return () => window.clearTimeout(timer);
  }, [attempt, loadHistory]);

  const generate = async () => {
    if (!preflight || inFlight.current || submitting || attempt || error) return;
    inFlight.current = true;
    setSubmitting(true);
    writeBrowserPreference(pendingKey, requestId.current);
    const actorId = useAuthStore.getState().user?.id;
    try {
      const value = await renderAnimationApi.generate({ project_id: projectId, source_render_id: render.id,
        request_id: requestId.current, confirm_paid_submission: true });
      acceptAttempt(value);
      if (mounted.current) setError(null);
    } catch (exc) {
      if (mounted.current) setError(getApiErrorMessage(exc, 'The submission response was interrupted. Reopen this panel to check the saved job.'));
      await loadHistory().catch(() => undefined);
    } finally {
      inFlight.current = false;
      if (mounted.current) setSubmitting(false);
      if (actorId) void authApi.me().then(user => {
        if (useAuthStore.getState().user?.id === actorId) useAuthStore.getState().setUser(user);
      }).catch(() => undefined);
    }
  };

  const videoUrl = attempt?.video_url ? resolveApiFileUrl(attempt.video_url) : null;
  const downloadUrl = videoUrl ? `${videoUrl}${videoUrl.includes('?') ? '&' : '?'}download=true&filename=city-prompt-animation-${attempt!.id.slice(0, 8)}.mp4` : null;
  return <div className="fixed inset-0 z-[350] flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
    onClick={onClose}>
    <section role="dialog" aria-modal="true" aria-labelledby="animate-render-title"
      className="max-h-[92dvh] w-full max-w-4xl overflow-y-auto rounded-2xl bg-[#f7f2e8] text-[#151515] shadow-2xl"
      onClick={event => event.stopPropagation()}>
      <header className="flex items-center gap-3 border-b border-black/10 px-5 py-4">
        <Film size={22} /><h2 id="animate-render-title" className="flex-1 text-lg font-bold">Animate this render</h2>
        <button ref={closeButton} type="button" onClick={onClose} aria-label="Close animation"
          className="flex min-h-11 min-w-11 items-center justify-center rounded-full hover:bg-black/10"><X size={20} /></button>
      </header>
      <div className="grid gap-5 p-5 md:grid-cols-[1.6fr_1fr]">
        <div className="min-w-0">
          {videoUrl ? <video src={videoUrl} controls autoPlay playsInline muted loop className="w-full rounded-xl bg-black" />
            : <img src={resolveApiFileUrl(render.image_url)} alt="Selected finished architectural render"
              className="max-h-[55vh] w-full rounded-xl bg-black object-contain" />}
          <p className="mt-2 text-xs text-black/60">{videoUrl ? 'Animated still · saved to this project' : 'Selected saved render · full-resolution source'}</p>
          {downloadUrl && <a href={downloadUrl} download className="mt-3 inline-flex min-h-11 items-center gap-2 rounded-full bg-[#151515] px-4 text-sm font-semibold text-white">
            <Download size={16} /> Download MP4</a>}
        </div>
        <div className="space-y-4">
          <div><p className="text-sm font-bold">A calm architectural film</p>
            <p className="mt-2 text-sm text-black/65">5 seconds · silent · slow camera push-in. Uses this finished image and keeps its lighting and colour treatment.</p>
            <p className="mt-2 text-xs text-black/60">AI motion may change details. Review the architecture before presenting.</p></div>
          {loading ? <p role="status" className="flex items-center gap-2 text-sm"><Loader2 size={16} className="animate-spin" /> Checking the saved render…</p>
            : !attempt && preflight && <div className="rounded-xl border border-black/10 bg-white p-3 text-sm">
              <p className="font-bold">{preflight.width} × {preflight.height} source</p>
              <p className="mt-1">{preflight.credit_cost} credits · provider estimate US${preflight.estimated_cost_usd.toFixed(2)}</p>
              <p className="mt-1 text-xs text-black/55">Creating a clip submits one paid generation.</p>
            </div>}
          {attempt ? <div className="rounded-xl bg-white p-3">
            <p role="status" className="text-sm font-bold">{attempt.status === 'complete' ? 'Your clip is ready' : attempt.status === 'submission_unknown'
              ? 'Submission needs review' : `Animation ${attempt.status.replace(/_/g, ' ')}`}</p>
            {attempt.recoverable && <p className="mt-2 text-xs text-black/60">You can close this panel. Reopen this render to check the same saved job.</p>}
            {attempt.recoverable && <button type="button" disabled={checking} onClick={() => void recover(attempt.id)}
              className="mt-3 inline-flex min-h-11 items-center gap-2 rounded-full border border-black/20 px-3 text-xs font-bold disabled:opacity-50">
              <RefreshCw size={14} className={checking ? 'animate-spin' : ''} /> Check saved request</button>}
          </div> : <button type="button" onClick={() => void generate()}
            disabled={loading || submitting || !preflight || !!error || preflight.attempts_remaining === 0}
            className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-full bg-[#28c7e8] px-4 py-3 text-sm font-bold hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-50">
            {submitting ? <Loader2 size={16} className="animate-spin" /> : <Film size={16} />}
            {submitting ? 'Submitting one clip…' : 'Create 5-second clip'}
          </button>}
          {(error || attempt?.error) && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error || attempt?.error}</p>}
        </div>
      </div>
    </section>
  </div>;
}
