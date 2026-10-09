import { PromptSpellingSuggestions } from './PromptSpellingSuggestions';
import { useCallback, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Cpu, Loader2, X } from 'lucide-react';
import { comfyTrialsApi, type ComfyJob, type ComfyPreset } from '@/services/comfyTrials';
import { getApiErrorMessage, resolveApiFileUrl } from '@/services/api';
import { savedRenderIsSource } from '@/utils/renderPresentation';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import type { SavedRender } from '@/types';
import type { VideoAttempt } from './VideoGeneratePanel';

interface Props {
  projectId: string; render: SavedRender; onSaved?: (attempt: VideoAttempt) => void; onImageSaved?: (render: SavedRender) => void;
}

export function LocalComfyTrialButton(props: Props) {
  const [open, setOpen] = useState(false);
  const close = useCallback(() => setOpen(false), []);
  if (!import.meta.env.DEV) return null;
  return <>
    <button type="button" onClick={() => setOpen(true)} className="inline-flex min-h-11 items-center gap-2 rounded-full bg-white px-3 py-2 text-xs font-bold text-slate-900 shadow-lg">
      <Cpu size={16} /> Local model trials
    </button>
    {open && createPortal(<LocalTrialDialog key={`${props.projectId}:${props.render.id}`} {...props} onClose={close} />, document.body)}
  </>;
}

function LocalTrialDialog({ projectId, render, onSaved, onImageSaved, onClose }: Props & { onClose: () => void }) {
  const [presets, setPresets] = useState<ComfyPreset[]>([]);
  const [presetId, setPresetId] = useState('flux-klein');
  const [prompt, setPrompt] = useState('');
  const [job, setJob] = useState<ComfyJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(false);
  const inFlight = useRef(false);
  const closeButton = useRef<HTMLButtonElement>(null);
  const dialog = useRef<HTMLDivElement>(null);
  const saved = useRef(onSaved);
  const imageSaved = useRef(onImageSaved);
  imageSaved.current = onImageSaved;
  saved.current = onSaved;
  const notified = useRef<string | null>(null);
  const pendingKey = `cityprompt.comfy.v1:${projectId}:${render.id}`;
  const requestId = useRef(readBrowserPreference(pendingKey) || crypto.randomUUID());
  const preset = presets.find(p => p.id === presetId);
  const isSource = savedRenderIsSource(render);
  const active = !!job && !['complete', 'failed'].includes(job.status);

  const accept = useCallback((value: ComfyJob) => {
    if (!mounted.current) return;
    setJob(value);
    if (value.status === 'complete') {
      writeBrowserPreference(pendingKey, null);
      if (value.result && notified.current !== value.id) {
        notified.current = value.id;
        if (value.kind === 'video') saved.current?.(value.result as VideoAttempt);
        else imageSaved.current?.(value.result as SavedRender);
      }
    }
  }, [pendingKey]);

  useEffect(() => {
    mounted.current = true;
    const focus = document.activeElement as HTMLElement | null;
    closeButton.current?.focus();
    const keydown = (event: KeyboardEvent) => {
      event.stopPropagation();
      if (event.key === 'Escape') onClose();
      if (event.key === 'Tab') {
        const controls = dialog.current?.querySelectorAll<HTMLElement>('button:not(:disabled), a[href], select:not(:disabled), textarea:not(:disabled), video[controls]');
        if (!controls?.length) return;
        const first = controls[0], last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener('keydown', keydown, true);
    void Promise.all([comfyTrialsApi.presets(), comfyTrialsApi.list(projectId)]).then(([models, history]) => {
      if (!mounted.current) return;
      setPresets(models.presets.filter(p => p.kind === 'image'));
      const previous = history.jobs.find(j => j.source_render_id === render.id && !['complete', 'failed'].includes(j.status))
        || history.jobs.find(j => j.request_id === requestId.current)
        || history.jobs.find(j => j.source_render_id === render.id);
      if (previous) { accept(previous); setPresetId(previous.preset); setPrompt(previous.prompt); }
      else {
        const first = models.presets.find(p => p.available && p.kind === 'image') || models.presets.find(p => p.kind === 'image');
        if (first) { setPresetId(first.id); setPrompt(first.default_prompt); }
      }
    }).catch(exc => {
      if (mounted.current) setError(getApiErrorMessage(exc, 'Could not check local models or saved jobs.'));
    }).finally(() => { if (mounted.current) setLoading(false); });
    return () => { mounted.current = false; document.removeEventListener('keydown', keydown, true); focus?.focus(); };
  }, [accept, isSource, onClose, projectId, render.id]);

  const recover = useCallback(async () => {
    if (!job || inFlight.current) return;
    inFlight.current = true; setBusy(true);
    try { const value = await comfyTrialsApi.recover(projectId, job.id); if (mounted.current) { setError(null); accept(value); } }
    catch (exc) { if (mounted.current) setError(getApiErrorMessage(exc, 'Could not check the original local job.')); }
    finally { inFlight.current = false; if (mounted.current) setBusy(false); }
  }, [accept, job, projectId]);

  useEffect(() => {
    if (!active || busy || error || job?.error) return;
    const timer = window.setTimeout(() => void recover(), 5000);
    return () => window.clearTimeout(timer);
  }, [active, busy, error, job, recover]);

  const generate = async () => {
    if (!preset?.available || !prompt.trim() || job || inFlight.current || (isSource && preset.kind === 'video')) return;
    inFlight.current = true; setBusy(true); setError(null);
    writeBrowserPreference(pendingKey, requestId.current);
    try {
      accept(await comfyTrialsApi.generate({ project_id: projectId, source_render_id: render.id, request_id: requestId.current, preset: presetId, prompt: prompt.trim() }));
    } catch (exc) {
      // Keep the same request ID after an ambiguous network response. Reopening
      // reads history; clicking again can only retrieve this same reservation.
      if (mounted.current) setError(getApiErrorMessage(exc, 'Could not submit. Reopen this panel to check the saved request.'));
    } finally { inFlight.current = false; if (mounted.current) setBusy(false); }
  };

  const resolveMissing = async () => {
    if (!job || inFlight.current) return;
    inFlight.current = true; setBusy(true);
    try { const value = await comfyTrialsApi.resolveMissing(projectId, job.id); if (mounted.current) { setError(null); accept(value); } }
    catch (exc) { if (mounted.current) setError(getApiErrorMessage(exc, 'Could not confirm the job is missing.')); }
    finally { inFlight.current = false; if (mounted.current) setBusy(false); }
  };

  const result = job?.result;
  const outputUrl = result && resolveApiFileUrl('image_url' in result ? result.image_url : result.video_url || '');
  return <div className="fixed inset-0 z-[350] flex items-center justify-center bg-black/75 p-4" onClick={onClose}>
    <div ref={dialog} role="dialog" aria-modal="true" aria-labelledby="comfy-trial-heading" className="max-h-[92vh] w-full max-w-4xl overflow-auto rounded-2xl bg-white p-5 text-slate-900 shadow-2xl" onClick={e => e.stopPropagation()}>
      <div className="flex items-center justify-between"><h2 id="comfy-trial-heading" className="text-lg font-bold">Local model trials</h2>
        <button ref={closeButton} aria-label="Close local trials" onClick={onClose} className="min-h-11 min-w-11"><X className="mx-auto" /></button></div>
      <p className="mb-4 text-sm text-slate-600">Runs on your desktop GPU · 0 CityPrompt credits. You can close this panel and return to the saved job.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <figure><img src={resolveApiFileUrl(render.image_url)} alt="Full saved source for local model trial" className="w-full rounded-lg" /><figcaption className="mt-1 text-xs text-slate-600">Selected saved image · model input is resized for your GPU.</figcaption></figure>
        <div>
          {loading ? <p role="status">Checking ComfyUI and saved jobs…</p> : <>
            <label className="block text-sm font-semibold" htmlFor="comfy-model">Model</label>
            <select id="comfy-model" value={presetId} disabled={busy || !!job} onChange={e => { setPresetId(e.target.value); setPrompt(presets.find(p => p.id === e.target.value)?.default_prompt || ''); }} className="mt-1 w-full rounded-lg border p-2">
              {job?.kind === 'video' && <option value={job.preset}>Archived local video trial</option>}
              {presets.map(p => <option key={p.id} value={p.id}>{p.label}{!p.available ? ' (unavailable)' : ''}</option>)}
            </select>
            <p className="my-2 break-words text-xs text-slate-600">{preset?.message}</p>
            {preset && <p className="mb-2 text-xs text-slate-600">Up to {preset.max_edge}px · {preset.steps} steps{preset.kind === 'video' ? ' · approximately 2 seconds · silent' : ''}</p>}
            {isSource && preset?.kind === 'video' && <p className="mb-2 text-sm">Select a finished image render to animate it. Finish this 3D source with an image model first.</p>}
            <label htmlFor="comfy-prompt" className="block text-sm font-semibold">Prompt</label>
            <textarea spellCheck={true} lang="en-CA" id="comfy-prompt" value={prompt} maxLength={1500} disabled={busy || !!job} onChange={e => setPrompt(e.target.value)} rows={5} className="mt-1 w-full rounded-lg border p-2 text-sm" />
            <PromptSpellingSuggestions value={prompt} onChange={setPrompt} disabled={busy || !!job} maxLength={1500} />
            {!job && <button onClick={() => void generate()} disabled={loading || busy || !!error || !preset?.available || !prompt.trim() || (isSource && preset.kind === 'video')} className="mt-3 min-h-11 rounded-lg bg-lime-300 px-4 font-semibold disabled:opacity-50">{busy ? 'Submitting…' : 'Run local trial'}</button>}
          </>}
          {job && <p role="status" className="mt-3 font-semibold">Local trial: {job.status}{busy && <Loader2 size={16} className="ml-2 inline animate-spin" />}</p>}
          {(error || job?.error) && <p role="alert" className="mt-2 text-sm text-red-700">{error || job?.error}</p>}
          {active && <button onClick={() => void recover()} disabled={busy} className="mt-2 min-h-11 rounded-lg border px-3">Check saved job</button>}
          {job?.status === 'submission_unknown' && <button onClick={() => void resolveMissing()} disabled={busy} className="ml-2 mt-2 min-h-11 rounded-lg border px-3">Mark missing job as failed</button>}
          {job && !active && <button onClick={() => { setJob(null); setError(null); if (job.kind === 'video' && presets[0]) { setPresetId(presets[0].id); setPrompt(presets[0].default_prompt); } requestId.current = crypto.randomUUID(); writeBrowserPreference(pendingKey, null); }} className="mt-2 min-h-11 rounded-lg border px-3">Set up another trial</button>}
        </div>
      </div>
      {outputUrl && <div className="mt-4 border-t pt-4"><p className="mb-2 text-sm font-semibold">Saved to this project’s gallery</p>
        {job?.kind === 'video' ? <video src={outputUrl} controls playsInline className="max-h-[45vh] w-full rounded-lg" /> : <img src={outputUrl} alt="Local model result" className="max-h-[45vh] w-full rounded-lg object-contain" />}
        <a href={outputUrl} download className="mt-2 inline-flex min-h-11 items-center underline">Download result</a>
        <p className="text-xs text-slate-600">AI interpretation · compare with the source before using it. Geometry preservation has not been verified.</p>
      </div>}
    </div>
  </div>;
}
