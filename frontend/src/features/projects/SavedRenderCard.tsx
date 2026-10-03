import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { getAssetTicketRevision, refreshAssetTickets, resolveApiFileUrl, subscribeAssetTicketChanges } from '@/services/api';
import type { SavedRender } from '@/types';
import { savedRenderIsSource, savedRenderNeedsReview } from '@/utils/renderPresentation';

export function savedRenderPreviewUrl(source: string): string {
  let url: URL;
  try { url = new URL(source, window.location.origin); } catch { return source; }
  const apiOrigin = new URL(import.meta.env.VITE_API_URL || window.location.origin, window.location.origin).origin;
  if (url.origin !== window.location.origin && url.origin !== apiOrigin) return source;
  if (!/^\/api\/v1\/files\/projects\/[^/]+\/renders\/[^/]+\.(png|jpe?g|webp)$/i.test(url.pathname)) return source;
  // Keep scoped credentials on the same URL; only ask for smaller pixels.
  url.searchParams.set('thumbnail', 'true');
  return url.href;
}

export function SavedRenderCard({ render, onSelect }: { render: SavedRender; onSelect: (render: SavedRender) => void }) {
  useSyncExternalStore(subscribeAssetTicketChanges, getAssetTicketRevision, getAssetTicketRevision);
  const source = resolveApiFileUrl(render.image_url);
  return <RenderPreview key={source} source={source} render={render} onSelect={onSelect} />;
}

function RenderPreview({ source, render, onSelect }: { source: string; render: SavedRender; onSelect: (render: SavedRender) => void }) {
  const [attempt, setAttempt] = useState(0);
  const [status, setStatus] = useState<'loading' | 'loaded' | 'failed'>('loading');
  const retrying = useRef(false);
  const alive = useRef(true);
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  const retry = async () => {
    if (retrying.current) return;
    retrying.current = true;
    setStatus('loading');
    try { await refreshAssetTickets(); } catch { /* The image request reports the remaining failure. */ }
    if (!alive.current) return;
    retrying.current = false;
    setAttempt(value => value + 1);
  };
  return <button type="button" onClick={() => status === 'failed' ? void retry() : onSelect(render)}
    aria-label={status === 'failed' ? 'Retry saved render preview' : `Open saved ${render.style || 'render'}`}
    className="group relative aspect-square overflow-hidden rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.03] text-left transition hover:border-amber-400/80">
    <img key={attempt} src={attempt === 0 ? savedRenderPreviewUrl(source) : source}
      alt="" loading="lazy" decoding="async"
      onLoad={() => setStatus('loaded')}
      onError={() => { if (attempt === 0) void retry(); else setStatus('failed'); }}
      className={`aspect-square w-full object-cover ${status === 'loaded' ? '' : 'opacity-0'}`} />
    {status !== 'loaded' && <span role="status" className="absolute inset-0 flex items-center justify-center p-3 text-center text-xs font-medium text-primary-950/70">
      {status === 'loading' ? 'Loading preview…' : 'Preview unavailable. Click to retry.'}
    </span>}
    {savedRenderNeedsReview(render) && <span className="absolute left-1 top-1 rounded bg-amber-100 px-1.5 py-1 text-[10px] font-bold text-amber-950">
      {render.variant === 'provider_original' ? 'AI render' : savedRenderIsSource(render) ? '3D source' : 'Compare with plan'}
    </span>}
    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/75 to-transparent p-2 opacity-0 transition group-hover:opacity-100">
      <p className="truncate text-[10px] font-semibold text-white">{render.style || 'render'}</p>
      <p className="text-[10px] text-white/65">{new Date(render.created_at).toLocaleDateString()}</p>
    </div>
  </button>;
}
