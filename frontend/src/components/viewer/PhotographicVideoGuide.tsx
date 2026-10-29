import { useCallback, useEffect, useRef, useState } from 'react';
import { direct3DAttempts, getApiErrorMessage } from '@/services/api';
import type { ImageAttempt } from '@/services/direct3DAttempts';

export interface PhotographicGuide {
  purpose: 'video_appearance'; attempt_id: string; image_base64: string;
  source_video_sha256: string; scene_revision_sha256: string; output_fingerprint: string;
  model: 'gpt-image-2.5-sunburst'; tokens_spent: number; signature: string;
}
export interface PhotographicGuideRequest {
  purpose: 'video_appearance'; project_id: string; beauty_image_base64: string;
  source_video_sha256: string; prompt?: string; details_revision?: number;
  community_3d_claims?: unknown[]; residual_landscape_claim?: unknown;
  authored_surface_claims?: Array<{ zone_id: string; source_hash: string }>;
  source_request?: unknown;
}

/** Hash decoded bytes, matching the backend, not the data-URL spelling. */
export async function videoBytesSha256(value: string): Promise<string> {
  const raw = atob(value.split(',').pop()!);
  const bytes = Uint8Array.from(raw, char => char.charCodeAt(0));
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), byte => byte.toString(16).padStart(2, '0')).join('');
}

export function PhotographicVideoGuide({ projectId, signature, guide, prepare, onChange, onBusyChange, onRestoreSource, automatic = false, disabled = false }: {
  projectId: string; signature: string; guide: PhotographicGuide | null;
  prepare: () => Promise<PhotographicGuideRequest>;
  onChange: (guide: PhotographicGuide | null) => void; onBusyChange: (busy: boolean) => void;
  onRestoreSource?: (source: unknown, guide: PhotographicGuide) => void;
  automatic?: boolean;
  disabled?: boolean;
}) {
  const [candidate, setCandidate] = useState<PhotographicGuide | null>(null);
  const [recoveredSource, setRecoveredSource] = useState<unknown>(null);
  const [attempts, setAttempts] = useState<ImageAttempt[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inFlight = useRef(false);
  const latestSignature = useRef(signature);
  latestSignature.current = signature;
  const mounted = useRef(true);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);
  const refresh = useCallback(async () => {
    try {
      const recent = await direct3DAttempts.list(projectId, 'video_appearance');
      if (mounted.current) setAttempts(recent.filter(a => a.style === 'video-appearance'));
    } catch { if (mounted.current) setError('Saved guides could not be checked. Reconnect before creating another.'); }
  }, [projectId]);
  useEffect(() => { void refresh(); }, [refresh]);
  const acceptResult = (result: Omit<PhotographicGuide, 'signature'>, startedSignature: string) => {
    if (!mounted.current) return;
    if (latestSignature.current !== startedSignature) {
      setError('The route changed. Your guide is saved. Recover it when using the original scene and route.');
      return;
    }
    setCandidate({ ...result, signature: startedSignature });
  };
  const create = async () => {
    if (inFlight.current || disabled) return;
    const startedSignature = signature;
    inFlight.current = true; setBusy(true); onBusyChange(true); setError(null); setCandidate(null); setRecoveredSource(null);
    if (guide) onChange(null);
    try {
      const request = await prepare();
      if (latestSignature.current !== startedSignature) throw new Error('The scene changed before submission. No guide was requested.');
      const result = await direct3DAttempts.generate<Omit<PhotographicGuide, 'signature'>>(request);
      acceptResult(result, startedSignature);
    } catch (err) { if (mounted.current) setError(getApiErrorMessage(err, 'The guide did not finish here. Recover saved guides before requesting another.')); }
    finally { inFlight.current = false; onBusyChange(false); if (mounted.current) { setBusy(false); void refresh(); } }
  };
  const recover = async (attempt: ImageAttempt) => {
    if (inFlight.current || disabled) return;
    inFlight.current = true; setBusy(true); onBusyChange(true); setError(null);
    const startedSignature = signature;
    try {
      if (attempt.status === 'completed') {
        const result = await direct3DAttempts.recover<Omit<PhotographicGuide, 'signature'>>(attempt);
        if (mounted.current) setRecoveredSource(result.source_request ?? null);
        acceptResult(result.response, startedSignature);
      } else if (attempt.status === 'failed' || attempt.status === 'unknown') {
        direct3DAttempts.acknowledge(attempt);
        setError(attempt.error?.message ?? 'This guide stopped. No automatic retry will occur.');
      }
      await refresh();
    } catch (err) { if (mounted.current) setError(getApiErrorMessage(err, 'Saved guide recovery is unavailable. Reconnect before generating again.')); }
    finally { inFlight.current = false; onBusyChange(false); if (mounted.current) setBusy(false); }
  };
  const preview = candidate?.signature === signature ? candidate : guide?.signature === signature ? guide : null;
  return <section className="mb-3 rounded-xl border-2 border-[#151515] bg-[#f7f2e8] p-3 text-[#151515]" aria-label="Photographic video finish">
    <p className="text-xs font-black">Photographic finish · Sunburst 2.5 → Omni 1.1</p>
    <p className="mt-1 text-[11px] leading-relaxed">{automatic ? 'Generate video prepares or reuses one matching photographic still for materials and daylight. The exact 3D route video controls camera, geometry and timing.' : 'Create and review one photographic still from your route, then use it to guide the film’s materials and daylight. The original 3D video controls layout and motion.'}</p>
    {!automatic && <button type="button" disabled={busy || disabled} onClick={() => void create()}
      className="mt-3 min-h-10 w-full rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 text-xs font-bold disabled:opacity-50">{busy ? 'Preparing saved guide…' : 'Create photographic guide · 26 tokens'}</button>
    }
    <p className="mt-1 text-[10px]">{automatic ? 'A new guide costs 26 tokens in addition to video. Preview, loading and changing options are free. No automatic paid retries.' : 'One paid image. Video is a separate paid step after review. No automatic paid retries.'}</p>
    {preview && <div className="mt-3">
      <img src={`data:image/png;base64,${preview.image_base64}`} alt="Photographic video guide to review" className="w-full rounded-lg border border-[#151515]/20" />
      <p className="mt-1 text-[10px]">Check buildings, people and skyline against the free route preview. The AI finish remains approximate.</p>
      <button type="button" disabled={busy || disabled} onClick={() => {
        if (recoveredSource && onRestoreSource) onRestoreSource(recoveredSource, preview);
        else onChange(preview);
      }} className="mt-2 min-h-10 w-full rounded-full border-2 border-[#151515] bg-white px-3 text-xs font-bold">{guide?.attempt_id === preview.attempt_id && guide.signature === signature ? 'Guide selected' : recoveredSource ? 'Use guide and restore original route' : 'Use this guide'}</button>
    </div>}
    {guide && guide.signature !== signature && <p className="mt-2 text-xs font-bold">The scene or route changed. {automatic ? 'Generate will prepare a matching guide after your next free preview.' : 'Prepare and review a matching guide.'}</p>}
    {error && <p role="alert" className="mt-2 text-xs text-red-700">{error}</p>}
    <details className="mt-3 text-xs"><summary className="cursor-pointer font-bold">Recover saved guides</summary>
      {automatic && <button type="button" disabled={busy || disabled} onClick={() => void create()} className="my-2 min-h-10 w-full rounded-lg border bg-white px-3">Prepare and review guide separately · 26 tokens</button>}
      <button type="button" disabled={busy || disabled} onClick={() => void refresh()} className="my-2 min-h-9 rounded-lg border px-3">Refresh guides · free</button>
      {attempts.map(attempt => <button key={attempt.id} type="button" disabled={busy || disabled} onClick={() => void recover(attempt)} className="mb-1 block min-h-10 w-full rounded-lg border bg-white p-2 text-left">{new Date(attempt.created_at).toLocaleString()} · {attempt.status} · {attempt.status === 'completed' ? 'Recover guide' : 'Check saved status'}</button>)}
      {!attempts.length && <p>No recent photographic guides.</p>}
    </details>
  </section>;
}
