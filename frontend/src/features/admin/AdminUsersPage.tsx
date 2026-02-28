import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2, Search, AlertTriangle, ShieldAlert, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '@/services/api';
import type { AdminUser } from '@/services/api';

interface RoleChangeModal {
  userId: string;
  email: string;
  newRole: string;
  type: 'promotion' | 'demotion';
}

export function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [roleModal, setRoleModal] = useState<RoleChangeModal | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.listUsers({
        search: search || undefined,
        role: roleFilter || undefined,
      });
      setUsers(data);
    } catch {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchUsers, 300);
    return () => clearTimeout(timer);
  }, [fetchUsers]);

  const applyRoleChange = async (userId: string, role: string) => {
    try {
      const updated = await adminApi.updateUser(userId, { role });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
      toast.success('Role updated');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update role');
    }
  };

  const handleRoleChange = (userId: string, role: string) => {
    const targetUser = users.find((u) => u.id === userId);
    if (!targetUser) return;

    // Promoting to admin — show confirmation modal
    if (role === 'admin' && targetUser.role !== 'admin') {
      setRoleModal({ userId, email: targetUser.email, newRole: role, type: 'promotion' });
      return;
    }

    // Demoting from admin — show confirmation modal
    if (targetUser.role === 'admin' && role !== 'admin') {
      setRoleModal({ userId, email: targetUser.email, newRole: role, type: 'demotion' });
      return;
    }

    applyRoleChange(userId, role);
  };

  const confirmRoleChange = () => {
    if (!roleModal) return;
    applyRoleChange(roleModal.userId, roleModal.newRole);
    setRoleModal(null);
  };

  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      const updated = await adminApi.updateUser(userId, { is_active: !isActive });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
      toast.success(isActive ? 'User deactivated' : 'User activated');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update user');
    }
  };

  const handleDeleteUser = async (userId: string, email: string) => {
    if (!window.confirm(`Permanently delete ${email}? This cannot be undone.`)) return;
    try {
      await adminApi.deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      toast.success('User deleted');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link to="/admin" className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Manage Users</h1>
      </div>

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by email or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        >
          <option value="">All roles</option>
          <option value="viewer">Viewer</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
        </div>
      ) : users.length === 0 ? (
        <p className="py-8 text-center text-sm text-gray-500">No users found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-xs font-medium uppercase text-gray-500">
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Projects</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Joined</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{u.full_name || '-'}</div>
                    <div className="text-xs text-gray-500">{u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="rounded border border-gray-200 px-2 py-1 text-xs focus:border-primary-500 focus:outline-none"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="editor">Editor</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{u.project_count}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        u.is_active
                          ? 'bg-green-50 text-green-700'
                          : 'bg-red-50 text-red-700'
                      }`}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 flex items-center gap-1">
                    <button
                      onClick={() => handleToggleActive(u.id, u.is_active)}
                      className={`rounded px-2 py-1 text-xs font-medium ${
                        u.is_active
                          ? 'text-red-600 hover:bg-red-50'
                          : 'text-green-600 hover:bg-green-50'
                      }`}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDeleteUser(u.id, u.email)}
                      className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600"
                      title="Delete user"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Role change confirmation modal */}
      {roleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center gap-3">
              {roleModal.type === 'promotion' ? (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-100">
                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                </div>
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
                  <ShieldAlert className="h-5 w-5 text-red-600" />
                </div>
              )}
              <h3 className="text-lg font-semibold text-gray-900">
                {roleModal.type === 'promotion' ? 'Grant Admin Access?' : 'Remove Admin Access?'}
              </h3>
            </div>
            <p className="mb-2 text-sm text-gray-600">
              {roleModal.type === 'promotion' ? (
                <>You are about to promote <strong className="text-gray-900">{roleModal.email}</strong> to <strong className="text-gray-900">Admin</strong>.</>
              ) : (
                <>You are about to demote <strong className="text-gray-900">{roleModal.email}</strong> from <strong className="text-gray-900">Admin</strong> to <strong className="text-gray-900 capitalize">{roleModal.newRole}</strong>.</>
              )}
            </p>
            <p className="mb-6 text-sm text-gray-500">
              {roleModal.type === 'promotion'
                ? 'This will give full platform access including user management. Are you sure?'
                : 'This will revoke their admin privileges. They will no longer be able to manage users or platform settings.'}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setRoleModal(null)}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmRoleChange}
                className={`rounded-lg px-4 py-2 text-sm font-medium text-white ${
                  roleModal.type === 'promotion'
                    ? 'bg-amber-600 hover:bg-amber-700'
                    : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                {roleModal.type === 'promotion' ? 'Yes, Grant Admin' : 'Yes, Remove Admin'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
