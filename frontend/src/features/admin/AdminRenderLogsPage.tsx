import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2, Search, Trash2, Eye, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '@/services/api';
import type { RenderAuditLog } from '@/services/api';

const API_BASE = import.meta.env.VITE_API_URL || '';

/** Fetch an image through the authenticated API and return an object URL */
function useAuthImage(url: string | undefined | null) {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    if (!url) { setSrc(null); return; }
    const token = localStorage.getItem('access_token');
    const fullUrl = url.startsWith('/') ? `${API_BASE}${url}` : url;
    fetch(fullUrl, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      .then((r) => r.ok ? r.blob() : Promise.reject())
      .then((blob) => setSrc(URL.createObjectURL(blob)))
      .catch(() => setSrc(null));
    return () => { if (src) URL.revokeObjectURL(src); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);
  return src;
}

function AuditImage({ url, label }: { url: string | null | undefined; label: string }) {
  const src = useAuthImage(url);
  const [lightbox, setLightbox] = useState(false);

  if (!src) return <span className="text-primary-950/30 text-xs">-</span>;

  return (
    <>
      <button
        onClick={() => setLightbox(true)}
        className="group relative h-12 w-16 overflow-hidden rounded border border-primary-950/[0.1] bg-primary-950/[0.04]"
      >
        <img src={src} alt={label} className="h-full w-full object-cover" />
        <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/30 transition-colors">
          <Eye size={14} className="text-white opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </button>
      {lightbox && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70" onClick={() => setLightbox(false)}>
          <div className="relative max-h-[90vh] max-w-[90vw]" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setLightbox(false)}
              className="absolute -right-3 -top-3 rounded-full bg-white p-1.5 shadow-lg hover:bg-gray-100"
            >
              <X size={16} />
            </button>
            <img src={src} alt={label} className="max-h-[85vh] max-w-[85vw] rounded-lg shadow-2xl" />
            <p className="mt-2 text-center text-sm text-white/70">{label}</p>
          </div>
        </div>
      )}
    </>
  );
}

export function AdminRenderLogsPage() {
  const [logs, setLogs] = useState<RenderAuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.listRenderLogs({
        user_email: search || undefined,
        limit: 100,
      });
      setLogs(data);
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
      setSelected(new Set(logs.map((l) => l.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (selected.size === 0) return;
    if (!confirm(`Delete ${selected.size} render log(s)? This also removes images from storage.`)) return;
    try {
      await adminApi.deleteRenderLogs(Array.from(selected));
      setLogs((prev) => prev.filter((l) => !selected.has(l.id)));
      toast.success(`Deleted ${selected.size} render log(s)`);
      setSelected(new Set());
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
          {logs.length} renders
        </span>
      </div>

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary-950/50" />
          <input
            type="text"
            placeholder="Filter by email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-primary-950/[0.1] bg-white py-2 pl-9 pr-3 text-sm text-primary-950 placeholder:text-primary-950/40 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
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

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
        </div>
      ) : logs.length === 0 ? (
        <p className="py-8 text-center text-sm text-primary-950/50">No render logs found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-primary-950/[0.08] text-left text-xs font-medium uppercase text-primary-950/50">
                <th className="px-3 py-3">
                  <input
                    type="checkbox"
                    checked={selected.size === logs.length && logs.length > 0}
                    onChange={toggleAll}
                    className="rounded border-primary-950/20"
                  />
                </th>
                <th className="px-3 py-3">User</th>
                <th className="px-3 py-3">Model</th>
                <th className="px-3 py-3">Tokens</th>
                <th className="px-3 py-3">Input</th>
                <th className="px-3 py-3">Output</th>
                <th className="px-3 py-3">Prompt</th>
                <th className="px-3 py-3">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-primary-950/[0.06]">
              {logs.map((log) => (
                <tr key={log.id} className={`hover:bg-white ${selected.has(log.id) ? 'bg-primary-500/[0.04]' : ''}`}>
                  <td className="px-3 py-3">
                    <input
                      type="checkbox"
                      checked={selected.has(log.id)}
                      onChange={() => toggleSelect(log.id)}
                      className="rounded border-primary-950/20"
                    />
                  </td>
                  <td className="px-3 py-3 text-primary-950/70">{log.user_email}</td>
                  <td className="px-3 py-3">
                    <span className="rounded-full bg-primary-950/[0.06] px-2 py-0.5 text-xs">{log.model.replace('gemini-', '').replace('-image', '').replace('-preview', '')}</span>
                  </td>
                  <td className="px-3 py-3 text-primary-950/50">{log.tokens_spent}</td>
                  <td className="px-3 py-2">
                    <AuditImage url={log.input_image_url} label="Input screenshot" />
                  </td>
                  <td className="px-3 py-2">
                    <AuditImage url={log.output_image_url} label="Render output" />
                  </td>
                  <td className="px-3 py-3 max-w-[200px]">
                    <p className="truncate text-xs text-primary-950/50" title={log.prompt_preview || ''}>
                      {log.prompt_preview ? log.prompt_preview.substring(0, 80) + '...' : '-'}
                    </p>
                  </td>
                  <td className="px-3 py-3 text-primary-950/50 whitespace-nowrap" title={new Date(log.created_at).toLocaleString()}>
                    {new Date(log.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
