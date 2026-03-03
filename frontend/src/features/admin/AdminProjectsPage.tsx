import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '@/services/api';
import type { AdminProject } from '@/services/api';

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-white/10 text-neutral-300',
  processing: 'bg-amber-500/15 text-amber-400',
  ready: 'bg-green-500/15 text-green-400',
  archived: 'bg-red-500/15 text-red-400',
};

export function AdminProjectsPage() {
  const [projects, setProjects] = useState<AdminProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.listAllProjects({
        search: search || undefined,
        status: statusFilter || undefined,
      });
      setProjects(data);
    } catch {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchProjects, 300);
    return () => clearTimeout(timer);
  }, [fetchProjects]);

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link to="/admin" className="rounded-lg p-1.5 text-neutral-400 hover:bg-white/10 hover:text-neutral-200">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-white">All Projects</h1>
      </div>

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
          <input
            type="text"
            placeholder="Search by project name or owner..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-white/[0.12] bg-white/[0.06] py-2 pl-9 pr-3 text-sm text-white placeholder:text-neutral-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-white/[0.12] bg-white/[0.06] px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="processing">Processing</option>
          <option value="ready">Ready</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
        </div>
      ) : projects.length === 0 ? (
        <p className="py-8 text-center text-sm text-neutral-400">No projects found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.08] text-left text-xs font-medium uppercase text-neutral-400">
                <th className="px-4 py-3">Project</th>
                <th className="px-4 py-3">Owner</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Buildings</th>
                <th className="px-4 py-3">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.08]">
              {projects.map((p) => (
                <tr key={p.id} className="hover:bg-white/[0.04]">
                  <td className="px-4 py-3">
                    <Link
                      to={`/projects/${p.id}`}
                      className="font-medium text-primary-400 hover:text-primary-300"
                    >
                      {p.name}
                    </Link>
                    {p.description && (
                      <p className="mt-0.5 truncate text-xs text-neutral-400" style={{ maxWidth: 300 }}>
                        {p.description}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="text-white">{p.owner_name || '-'}</div>
                    <div className="text-xs text-neutral-400">{p.owner_email}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[p.status] || 'bg-white/10 text-neutral-300'}`}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-neutral-400">{p.building_count}</td>
                  <td className="px-4 py-3 text-neutral-400">
                    {new Date(p.updated_at).toLocaleDateString()}
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
