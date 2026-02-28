import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, FolderOpen, Box, FileText, Loader2, BarChart3 } from 'lucide-react';
import { adminApi } from '@/services/api';
import type { AdminDashboardStats } from '@/services/api';
import { useAuthStore } from '@/store';

export function AdminDashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    adminApi
      .getStats()
      .then(setStats)
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load stats'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>;
  }

  if (!stats) return null;

  const cards = [
    { label: 'Total Users', value: stats.total_users, sub: `${stats.active_users} active`, icon: Users, color: 'text-blue-600 bg-blue-50', to: '/admin/users' },
    { label: 'Projects', value: stats.total_projects, icon: FolderOpen, color: 'text-green-600 bg-green-50', to: '/admin/projects' },
    { label: 'Buildings', value: stats.total_buildings, icon: Box, color: 'text-purple-600 bg-purple-50' },
    { label: 'Documents', value: stats.total_documents, icon: FileText, color: 'text-orange-600 bg-orange-50' },
  ];

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Admin Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          const content = (
            <div key={card.label} className="card flex items-center gap-4">
              <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${card.color}`}>
                <Icon size={24} />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                <p className="text-sm text-gray-500">{card.label}</p>
                {card.sub && <p className="text-xs text-gray-400">{card.sub}</p>}
              </div>
            </div>
          );
          return card.to ? (
            <Link key={card.label} to={card.to} className="transition-transform hover:scale-[1.02]">
              {content}
            </Link>
          ) : (
            <div key={card.label}>{content}</div>
          );
        })}
      </div>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">Users by Role</h2>
          <div className="space-y-2">
            {Object.entries(stats.users_by_role).map(([role, count]) => {
              const n = count as number;
              return (
                <div key={role} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-gray-600">{role}</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 rounded-full bg-primary-100" style={{ width: `${Math.max(20, (n / stats.total_users) * 200)}px` }}>
                      <div
                        className="h-2 rounded-full bg-primary-500"
                        style={{ width: '100%' }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">{n}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">Projects by Status</h2>
          <div className="space-y-2">
            {Object.entries(stats.projects_by_status).map(([s, count]) => {
              const n = count as number;
              const statusColors: Record<string, string> = {
                draft: 'bg-gray-500',
                processing: 'bg-yellow-500',
                ready: 'bg-green-500',
                archived: 'bg-red-400',
              };
              return (
                <div key={s} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-gray-600">{s}</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 rounded-full bg-gray-100" style={{ width: `${Math.max(20, (n / Math.max(stats.total_projects, 1)) * 200)}px` }}>
                      <div
                        className={`h-2 rounded-full ${statusColors[s] || 'bg-gray-400'}`}
                        style={{ width: '100%' }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">{n}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {user?.role === 'cofounder' && (
        <Link
          to="/admin/analytics"
          className="mt-8 flex items-center gap-4 rounded-xl border border-primary-200 bg-primary-50 p-5 transition-all hover:border-primary-300 hover:shadow-md"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
            <BarChart3 size={24} />
          </div>
          <div>
            <p className="text-lg font-semibold text-primary-900">Analytics Dashboard</p>
            <p className="text-sm text-primary-600">Deep platform insights, user trends, and system health</p>
          </div>
        </Link>
      )}
    </div>
  );
}
