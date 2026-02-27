import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Search, ArrowLeft, Building2, Clock } from 'lucide-react';
import { adminApi } from '@/services/api';

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  processing: 'bg-yellow-50 text-yellow-700',
  ready: 'bg-green-50 text-green-700',
  archived: 'bg-blue-50 text-blue-600',
};

export function AdminProjectsPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const { data: projects, isLoading } = useQuery({
    queryKey: ['admin', 'projects', search, statusFilter],
    queryFn: () =>
      adminApi.listAllProjects({
        search: search || undefined,
        status: statusFilter || undefined,
        limit: 100,
      }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/admin" className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">All Projects</h1>
          <p className="text-sm text-gray-500">{projects?.length ?? 0} projects across all users</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by project name or owner..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="processing">Processing</option>
          <option value="ready">Ready</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Project grid */}
      {isLoading ? (
        <div className="flex h-40 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects?.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="rounded-xl border border-gray-200 bg-white p-5 transition hover:border-blue-300 hover:shadow-sm"
            >
              <div className="mb-3 flex items-start justify-between">
                <h3 className="font-semibold text-gray-900 line-clamp-1">{project.name}</h3>
                <span className={`ml-2 shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[project.status] || ''}`}>
                  {project.status}
                </span>
              </div>

              {project.description && (
                <p className="mb-3 text-sm text-gray-500 line-clamp-2">{project.description}</p>
              )}

              <div className="space-y-1.5 text-xs text-gray-500">
                <div>
                  Owner: <span className="font-medium text-gray-700">{project.owner_name || project.owner_email}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Building2 size={12} />
                    {project.building_count} buildings
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    {new Date(project.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </Link>
          ))}
          {projects?.length === 0 && (
            <div className="col-span-full py-12 text-center text-gray-500">
              No projects found
            </div>
          )}
        </div>
      )}
    </div>
  );
}
