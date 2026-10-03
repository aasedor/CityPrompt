import { useCallback, useEffect, useRef, useState } from 'react';
import { direct3DAttempts, rendersApi } from '@/services/api';
import type { ImageAttempt, RecoveredImage } from '@/services/direct3DAttempts';
import { useAuthStore } from '@/store';
import { downloadDataImage } from '@/utils/downloadDataImage';
import { ImageFidelityReview, imageFidelityStatus } from './ImageFidelityReview';

type Recovery = RecoveredImage<Awaited<ReturnType<typeof rendersApi.generateDirect3D>>>;
const png = (value: string) => value.startsWith('data:') ? value : `data:image/png;base64,${value}`;

/** Recovery reads a saved attempt; opening this UI never generates an image. */
export function RecoverImageAttempts({ projectId }: { projectId: string }) {
  const userId = useAuthStore(state => state.user?.id);
  const [attempts, setAttempts] = useState<ImageAttempt[]>([]);
  const [enabled, setEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recovered, setRecovered] = useState<Recovery | null>(null);
  const revision = useRef(0);
  const refresh = useCallback(async () => {
    const current = revision.current;
    setLoading(true); setError('');
    try {
      const mode = await direct3DAttempts.capabilities();
      if (current !== revision.current) return;
      setEnabled(mode.enabled);
      if (mode.enabled) {
        const rows = await direct3DAttempts.list(projectId);
        if (current === revision.current) setAttempts(rows);
      }
    } catch { if (current === revision.current) setError('Could not check saved images. Reconnect and check again; no new image was requested.'); }
    finally { if (current === revision.current) setLoading(false); }
  }, [projectId]);
  useEffect(() => {
    revision.current += 1;
    setAttempts([]); setRecovered(null);
    void refresh();
    return () => { revision.current += 1; };
  }, [refresh, userId]);
  const open = async (attempt: ImageAttempt) => {
    const current = revision.current;
    setLoading(true); setError('');
    try {
      const image = await direct3DAttempts.recover<Recovery['response']>(attempt);
      if (current === revision.current) setRecovered(image);
    } catch { if (current === revision.current) setError('The saved image could not be opened. Check again later; generating a new image would use credits.'); }
    finally { if (current === revision.current) setLoading(false); }
  };
  if (!enabled && !error) return null;
  return <details className="border-b border-white/20 bg-slate-900 px-4 py-2 text-white">
    <summary className="min-h-11 cursor-pointer py-3 text-sm font-bold">Recover recent images</summary>
    <p className="text-xs text-white/80">An image keeps its original camera and design even if you edit the project. Checking or opening a saved image uses no image credits.</p>
    <button type="button" disabled={loading} onClick={() => void refresh()} className="my-2 min-h-11 rounded border border-white/40 px-3 text-sm">{loading ? 'Checking…' : 'Check saved images'}</button>
    {error && <p role="alert" className="text-sm text-amber-200">{error}</p>}
    {!loading && !error && attempts.length === 0 && <p className="pb-3 text-sm">No saved attempts for this account and project.</p>}
    {attempts.slice(0, 5).map(attempt => <div key={attempt.id} className="mb-3 rounded border border-white/20 p-2 text-sm">
      <p>{attempt.style} · {new Date(attempt.created_at).toLocaleString()} · {attempt.status === 'unknown' ? 'Interrupted' : attempt.status}</p>
      {(attempt.status === 'queued' || attempt.status === 'running') && <p className="text-xs text-white/80">Your request is saved. Check again shortly; avoid starting another image.</p>}
      {attempt.error && <p className="mt-1 text-amber-200">{attempt.error.message}</p>}
      {attempt.status === 'completed' && <button type="button" disabled={loading} onClick={() => void open(attempt)} className="mt-1 min-h-11 rounded border border-white/40 px-3">Open saved image</button>}
      {(attempt.status === 'failed' || attempt.status === 'unknown') && <button type="button" onClick={() => { direct3DAttempts.acknowledge(attempt); setError('Attempt acknowledged. A new image requires another explicit Generate click.'); }} className="mt-1 min-h-11 rounded border border-white/40 px-3">Acknowledge stopped attempt</button>}
    </div>)}
    {recovered && <section aria-label="Recovered image" className="space-y-3 pb-3">
      <ImageFidelityReview status={imageFidelityStatus(recovered.response.diagnostics)} warnings={recovered.response.warnings} />
      <figure><img src={png(recovered.source_image_base64)} alt="Original 3D design used for this saved image" /><figcaption className="text-xs">Original 3D view at the time of generation</figcaption></figure>
      <figure><img src={png(recovered.response.image_base64)} alt="Recovered image result for comparison with its original design" /><figcaption className="text-xs">Saved result · {recovered.style}</figcaption></figure>
      <button type="button" onClick={() => downloadDataImage(png(recovered.response.image_base64), `cityprompt-recovered-${recovered.attempt.id.slice(0, 8)}.png`)} className="min-h-11 rounded border border-white/40 px-3 text-sm">Download saved result</button>
      <button type="button" onClick={() => downloadDataImage(png(recovered.source_image_base64), `cityprompt-original-${recovered.attempt.id.slice(0, 8)}.png`)} className="ml-2 min-h-11 rounded border border-white/40 px-3 text-sm">Download original 3D view</button>
    </section>}
  </details>;
}
