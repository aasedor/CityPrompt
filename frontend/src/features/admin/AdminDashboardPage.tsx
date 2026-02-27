import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Users, FolderKanban, Building2, FileText, ArrowRight } from 'lucide-react';
import { adminApi } from '@/services/api';

export function AdminDashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: adminApi.getStats,
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    { label: 'Total Users', value: stats.total_users, sub: `${stats.active_users} active`, icon: Users, color: 'bg-blue-50 text-blue-600' },
    { label: 'Projects', value: stats.total_projects, icon: FolderKanban, color: 'bg-purple-50 text-purple-600' },
    { label: 'Buildings', value: stats.total_buildings, icon: Building2, color: 'bg-green-50 text-green-600' },
    { label: 'Documents', value: stats.total_documents, icon: FileText, color: 'bg-orange-50 text-orange-600' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">Platform overview and management</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div key={card.label} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center gap-3">
              <div className={`rounded-lg p-2 ${card.color}`}>
                <card.icon size={20} />
              </div>
              <div>
                <p className="text-sm text-gray-500">{card.label}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value.toLocaleString()}</p>
                {card.sub && <p className="text-xs text-gray-400">{card.sub}</p>}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Breakdowns */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Users by role */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Users by Role</h2>
          <div className="space-y-3">
            {Object.entries(stats.users_by_role).map(([role, count]) => (
              <div key={role} className="flex items-center justify-between">
                <span className="text-sm capitalize text-gray-600">{role}</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-24 rounded-full bg-gray-100">
                    <div
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${stats.total_users ? (count / stats.total_users) * 100 : 0}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Projects by status */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Projects by Status</h2>
          <div className="space-y-3">
            {Object.entries(stats.projects_by_status).map(([projectStatus, count]) => (
              <div key={projectStatus} className="flex items-center justify-between">
                <span className="text-sm capitalize text-gray-600">{projectStatus}</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-24 rounded-full bg-gray-100">
                    <div
                      className="h-2 rounded-full bg-purple-500"
                      style={{ width: `${stats.total_projects ? (count / stats.total_projects) * 100 : 0}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Link
          to="/admin/users"
          className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-5 transition hover:border-blue-300 hover:shadow-sm"
        >
          <div className="flex items-center gap-3">
            <Users size={20} className="text-blue-600" />
            <span className="font-medium text-gray-900">Manage Users</span>
          </div>
          <ArrowRight size={16} className="text-gray-400" />
        </Link>
        <Link
          to="/admin/projects"
          className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-5 transition hover:border-purple-300 hover:shadow-sm"
        >
          <div className="flex items-center gap-3">
            <FolderKanban size={20} className="text-purple-600" />
            <span className="font-medium text-gray-900">All Projects</span>
          </div>
          <ArrowRight size={16} className="text-gray-400" />
        </Link>
      </div>
    </div>
  );
}
