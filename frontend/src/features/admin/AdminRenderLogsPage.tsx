import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowLeftRight, Loader2, Search, Trash2, Eye, X, ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '@/services/api';
import type { RenderAuditLog, RenderLogStats } from '@/services/api';

const API_BASE = import.meta.env.VITE_API_URL || '';
const RENDER_LOG_PAGE_SIZE = 200;

function useAuthImage(url: string | undefined | null, enabled: boolean) {
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;

    if (!url || !enabled) {
      setSrc((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return null;
      });
      return () => {};
    }

    const token = localStorage.getItem('access_token');
    const fullUrl = url.startsWith('/') ? `${API_BASE}${url}` : url;

    fetch(fullUrl, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      .then((r) => (r.ok ? r.blob() : Promise.reject()))
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setSrc((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return objectUrl;
        });
      })
      .catch(() => {
        if (!cancelled) {
          setSrc((prev) => {
            if (prev) URL.revokeObjectURL(prev);
            return null;
          });
        }
      });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [url, enabled]);

  return src;
}

function useInView(ref: React.RefObject<HTMLElement>, rootMargin = '200px') {
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { rootMargin },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [ref, rootMargin]);

  return inView;
}

function AuditImage({
  url,
  label,
  onClick,
  eager,
}: {
  url: string | null | undefined;
  label: string;
  onClick?: () => void;
  eager?: boolean;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const visible = useInView(ref);
  const src = useAuthImage(url, Boolean(eager || visible));

  return (
    <span ref={ref} className="inline-block">
      {src ? (
        <button
          onClick={onClick}
          className="group relative h-12 w-16 cursor-pointer overflow-hidden rounded border border-primary-950/[0.1] bg-primary-950/[0.04]"
          title={`Click to view ${label}`}
        >
          <img src={src} alt={label} className="h-full w-full object-cover" />
          <div className="absolute inset-0 flex items-center justify-center bg-black/0 transition-colors group-hover:bg-black/30">
            <Eye size={14} className="text-white opacity-0 transition-opacity group-hover:opacity-100" />
          </div>
        </button>
      ) : (
        <span className="flex h-12 w-16 items-center justify-center rounded border border-primary-950/[0.06] bg-primary-950/[0.02]">
          <span className="text-xs text-primary-950/20">{visible || eager ? '...' : '-'}</span>
        </span>
      )}
    </span>
  );
}

function CompareLightbox({
  inputUrl,
  outputUrl,
  startOnOutput = false,
  onClose,
}: {
  inputUrl: string | null | undefined;
  outputUrl: string | null | undefined;
  startOnOutput?: boolean;
  onClose: () => void;
}) {
  const [showOutput, setShowOutput] = useState(startOnOutput);
  const inputSrc = useAuthImage(inputUrl, true);
  const outputSrc = useAuthImage(outputUrl, true);
  const currentSrc = showOutput ? outputSrc : inputSrc;
  const label = showOutput ? 'Output (render)' : 'Input (screenshot)';

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') setShowOutput(false);
      else if (e.key === 'ArrowRight') setShowOutput(true);
      else if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  if (!currentSrc) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={onClose}>
      <div className="relative flex flex-col items-center" onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className="absolute -right-3 -top-3 z-10 rounded-full bg-white p-1.5 shadow-lg hover:bg-gray-100">
          <X size={16} />
        </button>

        <div className="relative">
          <img src={currentSrc} alt={label} className="max-h-[80vh] max-w-[85vw] rounded-lg shadow-2xl" />

          {inputSrc && (
            <button
              onClick={() => setShowOutput(false)}
              className={`absolute left-3 top-1/2 -translate-y-1/2 rounded-full p-2 transition-all ${
                !showOutput ? 'bg-white text-primary-950 shadow-lg' : 'bg-black/40 text-white/70 hover:bg-black/60 hover:text-white'
              }`}
            >
              <ChevronLeft size={20} />
            </button>
          )}

          {outputSrc && (
            <button
              onClick={() => setShowOutput(true)}
              className={`absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 transition-all ${
                showOutput ? 'bg-white text-primary-950 shadow-lg' : 'bg-black/40 text-white/70 hover:bg-black/60 hover:text-white'
              }`}
            >
              <ChevronRight size={20} />
            </button>
          )}
        </div>

        <div className="mt-3 flex items-center gap-3">
          <button
            onClick={() => setShowOutput(false)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-all ${
              !showOutput ? 'bg-white text-primary-950' : 'bg-white/10 text-white/60 hover:text-white'
            }`}
          >
            Input
          </button>
          <ArrowLeftRight size={14} className="text-white/40" />
          <button
            onClick={() => setShowOutput(true)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-all ${
              showOutput ? 'bg-white text-primary-950' : 'bg-white/10 text-white/60 hover:text-white'
            }`}
          >
            Output
          </button>
        </div>
        <p className="mt-1 text-xs text-white/40">Left/Right switches image. Up/Down changes render.</p>
      </div>
    </div>
  );
}

function ExpandedLogDetail({
  log,
  onCompare,
}: {
  log: RenderAuditLog;
  onCompare: (output: boolean) => void;
}) {
  const inputThumbSrc = useAuthImage(log.input_thumbnail_url ?? log.input_image_url, true);
  const outputThumbSrc = useAuthImage(log.output_thumbnail_url ?? log.output_image_url, true);

  return (
    <div className="flex gap-6 p-4">
      <div className="flex gap-3">
        {inputThumbSrc ? (
          <button
            onClick={() => onCompare(false)}
            className="group relative h-40 w-52 cursor-pointer overflow-hidden rounded-lg border border-primary-950/[0.1] bg-primary-950/[0.04]"
          >
            <img src={inputThumbSrc} alt="Input" className="h-full w-full object-cover" />
            <span className="absolute bottom-1.5 left-1.5 rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-white">Input</span>
            <div className="absolute inset-0 flex items-center justify-center bg-black/0 transition-colors group-hover:bg-black/30">
              <Eye size={20} className="text-white opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          </button>
        ) : (
          <div className="flex h-40 w-52 items-center justify-center rounded-lg border border-dashed border-primary-950/[0.1]">
            <Loader2 size={16} className="animate-spin text-primary-950/20" />
          </div>
        )}

        {outputThumbSrc ? (
          <button
            onClick={() => onCompare(true)}
            className="group relative h-40 w-52 cursor-pointer overflow-hidden rounded-lg border border-primary-950/[0.1] bg-primary-950/[0.04]"
          >
            <img src={outputThumbSrc} alt="Output" className="h-full w-full object-cover" />
            <span className="absolute bottom-1.5 left-1.5 rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-white">Output</span>
            <div className="absolute inset-0 flex items-center justify-center bg-black/0 transition-colors group-hover:bg-black/30">
              <Eye size={20} className="text-white opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          </button>
        ) : (
          <div className="flex h-40 w-52 items-center justify-center rounded-lg border border-dashed border-primary-950/[0.1]">
            <Loader2 size={16} className="animate-spin text-primary-950/20" />
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <p className="mb-1 text-xs font-medium uppercase text-primary-950/40">Full Prompt</p>
        <p className="max-h-36 overflow-y-auto whitespace-pre-wrap break-words text-sm leading-relaxed text-primary-950/70">
          {log.prompt_preview || 'No prompt recorded'}
        </p>
      </div>
    </div>
  );
}

export function AdminRenderLogsPage() {
  const [logs, setLogs] = useState<RenderAuditLog[]>([]);
  const [stats, setStats] = useState<RenderLogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [compareLog, setCompareLog] = useState<RenderAuditLog | null>(null);
  const [compareStartOutput, setCompareStartOutput] = useState(false);

  const rowRefs = useRef<Map<string, HTMLTableRowElement>>(new Map());
  const expandedIdRef = useRef<string | null>(null);
  const logsRef = useRef<RenderAuditLog[]>([]);
  const compareLogRef = useRef<RenderAuditLog | null>(null);

  expandedIdRef.current = expandedId;
  logsRef.current = logs;
  compareLogRef.current = compareLog;

  const fetchStats = useCallback(() => {
    adminApi.renderLogStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.listRenderLogs({
        user_email: search || undefined,
        limit: RENDER_LOG_PAGE_SIZE,
      });
      setLogs(data);
      setHasMore(data.length === RENDER_LOG_PAGE_SIZE);
      setSelected(new Set());
      setExpandedId(null);
    } catch {
      toast.error('Failed to load render logs');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const timer = setTimeout(fetchLogs, 300);
    return () => clearTimeout(timer);
  }, [fetchLogs]);

  const toggleExpand = useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  const loadMoreLogs = useCallback(async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const data = await adminApi.listRenderLogs({
        user_email: search || undefined,
        skip: logs.length,
        limit: RENDER_LOG_PAGE_SIZE,
      });
      setLogs((prev) => [...prev, ...data]);
      setHasMore(data.length === RENDER_LOG_PAGE_SIZE);
    } catch {
      toast.error('Failed to load more render logs');
    } finally {
      setLoadingMore(false);
    }
  }, [hasMore, loadingMore, logs.length, search]);

  const loadAllLogs = useCallback(async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      let skip = logsRef.current.length;
      let nextHasMore = true;

      while (nextHasMore) {
        const data = await adminApi.listRenderLogs({
          user_email: search || undefined,
          skip,
          limit: RENDER_LOG_PAGE_SIZE,
        });

        if (data.length > 0) {
          setLogs((prev) => [...prev, ...data]);
        }

        skip += data.length;
        nextHasMore = data.length === RENDER_LOG_PAGE_SIZE;
      }

      setHasMore(false);
    } catch {
      toast.error('Failed to load all render logs');
    } finally {
      setLoadingMore(false);
    }
  }, [hasMore, loadingMore, search]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;

      const target = e.target as HTMLElement | null;
      if (
        target
        && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName))
      ) {
        return;
      }

      const currentLogs = logsRef.current;
      if (currentLogs.length === 0) return;

      e.preventDefault();

      const activeLightbox = compareLogRef.current;
      if (activeLightbox) {
        const idx = currentLogs.findIndex((log) => log.id === activeLightbox.id);
        const next = e.key === 'ArrowDown'
          ? (idx < currentLogs.length - 1 ? idx + 1 : 0)
          : (idx > 0 ? idx - 1 : currentLogs.length - 1);
        const nextLog = currentLogs[next];
        if (nextLog) setCompareLog(nextLog);
        return;
      }

      const currentId = expandedIdRef.current;
      const idx = currentId ? currentLogs.findIndex((log) => log.id === currentId) : -1;
      const next = e.key === 'ArrowDown'
        ? (idx < currentLogs.length - 1 ? idx + 1 : 0)
        : (idx > 0 ? idx - 1 : currentLogs.length - 1);
      const nextId = currentLogs[next]?.id;
      if (nextId) {
        setExpandedId(nextId);
        rowRefs.current.get(nextId)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (selected.size === logs.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(logs.map((log) => log.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (selected.size === 0) return;
    if (!confirm(`Delete ${selected.size} render log(s)? This also removes images from storage.`)) return;
    try {
      await adminApi.deleteRenderLogs(Array.from(selected));
      setLogs((prev) => prev.filter((log) => !selected.has(log.id)));
      toast.success(`Deleted ${selected.size} render log(s)`);
      setSelected(new Set());
      fetchStats();
    } catch {
      toast.error('Failed to delete render logs');
    }
  };

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link to="/admin" className="rounded-lg p-1.5 text-primary-950/50 hover:bg-primary-950/[0.04] hover:text-primary-950/70">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-primary-950">Render Audit Logs</h1>
        <span className="rounded-full bg-primary-950/[0.06] px-2.5 py-0.5 text-xs font-medium text-primary-950/50">
          {logs.length}{hasMore ? '+' : ''} renders
        </span>
      </div>

      {stats && (
        <div className="mb-4 rounded-xl border border-primary-950/[0.08] bg-white p-4">
          <div className="flex flex-wrap items-center gap-6">
            <div>
              <p className="text-xs font-medium uppercase text-primary-950/40">Total Renders</p>
              <p className="text-xl font-bold text-primary-950">{stats.total_renders.toLocaleString()}</p>
            </div>
            <div className="min-w-[200px] flex-1">
              <div className="mb-1 flex items-center justify-between">
                <p className="text-xs font-medium uppercase text-primary-950/40">Storage Used</p>
                <p className="text-xs font-medium text-primary-950/60">
                  {stats.storage_gb < 1 ? `${stats.storage_mb} MB` : `${stats.storage_gb} GB`} / {stats.storage_limit_gb} GB
                </p>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-primary-950/[0.06]">
                <div
                  className={`h-full rounded-full transition-all ${
                    stats.storage_gb / stats.storage_limit_gb > 0.8
                      ? 'bg-red-500'
                      : stats.storage_gb / stats.storage_limit_gb > 0.5
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.max(stats.storage_bytes > 0 ? 2 : 0, Math.min(100, (stats.storage_gb / stats.storage_limit_gb) * 100))}%` }}
                />
              </div>
            </div>
            {stats.oldest_render && (
              <div>
                <p className="text-xs font-medium uppercase text-primary-950/40">Since</p>
                <p className="text-sm font-medium text-primary-950/60">{new Date(stats.oldest_render).toLocaleDateString()}</p>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-md flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary-950/50" />
          <input
            type="text"
            placeholder="Filter by email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-primary-950/[0.1] bg-white py-2 pl-9 pr-3 text-sm text-primary-950 placeholder:text-primary-950/40 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-primary-950/30">Up/Down to navigate</span>
          {selected.size > 0 && (
            <button
              onClick={handleBulkDelete}
              className="flex items-center gap-1.5 rounded-lg bg-red-500/10 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-500/20"
            >
              <Trash2 size={14} />
              Delete {selected.size} selected
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
        </div>
      ) : logs.length === 0 ? (
        <p className="py-8 text-center text-sm text-primary-950/50">No render logs found.</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-primary-950/[0.08] text-left text-xs font-medium uppercase text-primary-950/50">
                  <th className="w-8 px-3 py-3">
                    <input
                      type="checkbox"
                      checked={selected.size === logs.length && logs.length > 0}
                      onChange={toggleAll}
                      className="rounded border-primary-950/20"
                    />
                  </th>
                  <th className="px-3 py-3">User</th>
                  <th className="px-3 py-3">Project</th>
                  <th className="px-3 py-3">Model</th>
                  <th className="px-3 py-3">Tokens</th>
                  <th className="px-3 py-3">Preview</th>
                  <th className="px-3 py-3">Prompt</th>
                  <th className="px-3 py-3">Time</th>
                  <th className="w-8 px-3 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-primary-950/[0.06]">
                {logs.map((log) => {
                  const isExpanded = expandedId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr
                        ref={(el) => {
                          if (el) rowRefs.current.set(log.id, el);
                          else rowRefs.current.delete(log.id);
                        }}
                        className={`group cursor-pointer transition-colors ${
                          isExpanded
                            ? 'bg-primary-500/[0.04]'
                            : selected.has(log.id)
                              ? 'bg-primary-500/[0.02]'
                              : 'hover:bg-primary-950/[0.02]'
                        }`}
                      >
                        <td className="px-3 py-3 align-top" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="checkbox"
                            checked={selected.has(log.id)}
                            onChange={() => toggleSelect(log.id)}
                            className="rounded border-primary-950/20"
                          />
                        </td>
                        <td className="px-3 py-3 align-top text-primary-950/70" onClick={() => toggleExpand(log.id)}>
                          {log.user_email}
                        </td>
                        <td className="max-w-[180px] px-3 py-3 align-top" onClick={() => toggleExpand(log.id)}>
                          {log.project_id ? (
                            <Link
                              to={`/projects/${log.project_id}`}
                              onClick={(e) => e.stopPropagation()}
                              className="block truncate font-medium text-primary-700 hover:text-coral-500 hover:underline"
                              title={log.project_name || log.project_id}
                            >
                              {log.project_name || 'Open project'}
                            </Link>
                          ) : (
                            <span className="text-primary-950/30">-</span>
                          )}
                        </td>
                        <td className="px-3 py-3 align-top" onClick={() => toggleExpand(log.id)}>
                          <span className="rounded-full bg-primary-950/[0.06] px-2 py-0.5 text-xs">
                            {log.model.replace('gemini-', '').replace('-image', '').replace('-preview', '')}
                          </span>
                        </td>
                        <td className="px-3 py-3 align-top text-primary-950/50" onClick={() => toggleExpand(log.id)}>
                          {log.tokens_spent}
                        </td>
                        <td className="px-3 py-2 align-top">
                          <div className="flex items-center gap-1.5">
                            <AuditImage url={log.input_thumbnail_url ?? log.input_image_url} label="Input" onClick={() => { setCompareStartOutput(false); setCompareLog(log); }} />
                            <AuditImage url={log.output_thumbnail_url ?? log.output_image_url} label="Output" onClick={() => { setCompareStartOutput(true); setCompareLog(log); }} />
                          </div>
                        </td>
                        <td className="max-w-[200px] px-3 py-3 align-top" onClick={() => toggleExpand(log.id)}>
                          <p className="truncate text-xs text-primary-950/50" title={log.prompt_preview || ''}>
                            {log.prompt_preview ? `${log.prompt_preview.substring(0, 80)}...` : '-'}
                          </p>
                        </td>
                        <td className="whitespace-nowrap px-3 py-3 align-top text-primary-950/50" onClick={() => toggleExpand(log.id)} title={new Date(log.created_at).toLocaleString()}>
                          {new Date(log.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-3 py-3 align-top" onClick={() => toggleExpand(log.id)}>
                          <ChevronDown size={14} className={`text-primary-950/30 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-primary-50/50">
                          <td colSpan={9} className="p-0">
                            <ExpandedLogDetail
                              log={log}
                              onCompare={(output) => { setCompareStartOutput(output); setCompareLog(log); }}
                            />
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>

          {hasMore && (
            <div className="mt-4 flex flex-wrap items-center justify-center gap-3 border-t border-primary-950/[0.06] pt-4">
              <button
                onClick={loadMoreLogs}
                disabled={loadingMore}
                className="flex items-center gap-2 rounded-lg border border-primary-950/[0.1] bg-white px-4 py-2 text-sm font-medium text-primary-950/70 hover:bg-primary-950/[0.03] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingMore ? <Loader2 size={14} className="animate-spin" /> : null}
                Load more
              </button>
              <button
                onClick={loadAllLogs}
                disabled={loadingMore}
                className="flex items-center gap-2 rounded-lg bg-primary-950 px-4 py-2 text-sm font-medium text-white hover:bg-primary-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingMore ? <Loader2 size={14} className="animate-spin" /> : null}
                Load all
              </button>
              <span className="text-xs text-primary-950/40">
                Showing {logs.length} logs
              </span>
            </div>
          )}
        </>
      )}

      {compareLog && (
        <CompareLightbox
          inputUrl={compareLog.input_image_url}
          outputUrl={compareLog.output_image_url}
          startOnOutput={compareStartOutput}
          onClose={() => setCompareLog(null)}
        />
      )}
    </div>
  );
}
