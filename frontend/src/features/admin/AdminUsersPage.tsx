import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Crown, Loader2, Search, AlertTriangle, ShieldAlert, Trash2, Plus, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '@/services/api';
import type { AdminUser } from '@/services/api';
import { useAuthStore } from '@/store';

interface RoleChangeModal {
  userId: string;
  email: string;
  newRole: string;
  type: 'promotion' | 'demotion';
}

export function AdminUsersPage() {
  const { user: currentUser } = useAuthStore();
  const isCofounder = currentUser?.role === 'cofounder';
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
      if (updated._email_failed) {
        toast.success('Role updated, but welcome email failed to send', { duration: 4000 });
      } else {
        toast.success(['admin', 'cofounder'].includes(role) ? 'Role updated — welcome email sent' : 'Role updated');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update role');
    }
  };

  const handleRoleChange = (userId: string, role: string) => {
    const targetUser = users.find((u) => u.id === userId);
    if (!targetUser) return;

    // Promoting to admin or cofounder — show confirmation modal
    if (['admin', 'cofounder'].includes(role) && !['admin', 'cofounder'].includes(targetUser.role)) {
      setRoleModal({ userId, email: targetUser.email, newRole: role, type: 'promotion' });
      return;
    }

    // Promoting admin to cofounder
    if (role === 'cofounder' && targetUser.role === 'admin') {
      setRoleModal({ userId, email: targetUser.email, newRole: role, type: 'promotion' });
      return;
    }

    // Demoting from admin or cofounder — show confirmation modal
    if (['admin', 'cofounder'].includes(targetUser.role) && !['admin', 'cofounder'].includes(role)) {
      setRoleModal({ userId, email: targetUser.email, newRole: role, type: 'demotion' });
      return;
    }

    // Demoting cofounder to admin
    if (targetUser.role === 'cofounder' && role === 'admin') {
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
        <Link to="/admin" className="rounded-lg p-1.5 text-primary-950/50 hover:bg-primary-950/[0.04] hover:text-primary-950/70">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-primary-950">Manage Users</h1>
      </div>

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary-950/50" />
          <input
            type="text"
            placeholder="Search by email or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-primary-950/[0.1] bg-white py-2 pl-9 pr-3 text-sm text-primary-950 placeholder:text-primary-950/40 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-primary-950 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          <option value="">All roles</option>
          <option value="viewer">Viewer</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
          <option value="cofounder">Cofounder</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
        </div>
      ) : users.length === 0 ? (
        <p className="py-8 text-center text-sm text-primary-950/50">No users found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-primary-950/[0.08] text-left text-xs font-medium uppercase text-primary-950/50">
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Projects</th>
                <th className="px-4 py-3">Tokens</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Last Login</th>
                <th className="px-4 py-3">Joined</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-primary-950/[0.06]">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-white">
                  <td className="px-4 py-3">
                    <div className="font-medium text-primary-950">{u.full_name || '-'}</div>
                    <div className="text-xs text-primary-950/50">{u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      disabled={!isCofounder && ['admin', 'cofounder'].includes(u.role)}
                      className="rounded border border-primary-950/[0.1] bg-white px-2 py-1 text-xs text-primary-950 focus:border-primary-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="editor">Editor</option>
                      <option value="admin">Admin</option>
                      {isCofounder && <option value="cofounder">Cofounder</option>}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-primary-950/50">{u.project_count}</td>
                  <td className="px-4 py-3">
                    {['admin', 'cofounder'].includes(u.role) ? (
                      <span className="text-xs text-primary-950/40">Unlimited</span>
                    ) : (
                      <div className="flex items-center gap-1.5">
                        <div className="w-16 h-1.5 rounded-full bg-primary-950/[0.08] overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              u.render_credits > 500 ? 'bg-emerald-500' : u.render_credits > 100 ? 'bg-amber-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min(100, (u.render_credits / 1000) * 100)}%` }}
                          />
                        </div>
                        <span className={`text-xs font-medium ${
                          u.render_credits > 500 ? 'text-emerald-600' : u.render_credits > 100 ? 'text-amber-600' : 'text-red-500'
                        }`}>
                          {u.render_credits.toLocaleString()}
                        </span>
                        <span className="text-[10px] text-primary-950/30">/ 1,000</span>
                        <button
                          onClick={() => {
                            const amt = prompt('Add tokens:', '500');
                            if (amt && !isNaN(Number(amt)) && Number(amt) > 0) {
                              adminApi.updateTokens(u.id, Number(amt), 'add').then((updated) => {
                                setUsers((prev) => prev.map((x) => x.id === updated.id ? updated : x));
                                toast.success(`Added ${amt} tokens to ${u.email}`);
                              }).catch(() => toast.error('Failed to add tokens'));
                            }
                          }}
                          className="rounded p-0.5 text-primary-950/40 hover:bg-emerald-500/15 hover:text-emerald-600"
                          title="Add tokens"
                        >
                          <Plus size={13} />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Reset ${u.email} to 1,000 tokens?`)) {
                              adminApi.updateTokens(u.id, 1000, 'set').then((updated) => {
                                setUsers((prev) => prev.map((x) => x.id === updated.id ? updated : x));
                                toast.success(`Reset ${u.email} to 1,000 tokens`);
                              }).catch(() => toast.error('Failed to reset tokens'));
                            }
                          }}
                          className="rounded p-0.5 text-primary-950/40 hover:bg-primary-500/15 hover:text-primary-600"
                          title="Reset to 1,000 tokens"
                        >
                          <RotateCcw size={13} />
                        </button>
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        u.is_active
                          ? 'bg-green-500/15 text-green-400'
                          : 'bg-red-500/15 text-red-600'
                      }`}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-primary-950/50">
                    {u.last_login_at
                      ? new Date(u.last_login_at).toLocaleDateString()
                      : <span className="text-primary-950/40">Never</span>}
                  </td>
                  <td className="px-4 py-3 text-primary-950/50">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 flex items-center gap-1">
                    <button
                      onClick={() => handleToggleActive(u.id, u.is_active)}
                      className={`rounded px-2 py-1 text-xs font-medium ${
                        u.is_active
                          ? 'text-red-600 hover:bg-red-500/15'
                          : 'text-green-400 hover:bg-green-500/15'
                      }`}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDeleteUser(u.id, u.email)}
                      className="rounded p-1 text-primary-950/50 hover:bg-red-500/15 hover:text-red-600"
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="mx-4 w-full max-w-md rounded-xl bg-white border border-primary-950/[0.08] p-6 shadow-xl backdrop-blur-xl">
            <div className="mb-4 flex items-center gap-3">
              {roleModal.type === 'promotion' ? (
                roleModal.newRole === 'cofounder' ? (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500/15">
                    <Crown className="h-5 w-5 text-yellow-400" />
                  </div>
                ) : (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/15">
                    <AlertTriangle className="h-5 w-5 text-amber-400" />
                  </div>
                )
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/15">
                  <ShieldAlert className="h-5 w-5 text-red-600" />
                </div>
              )}
              <h3 className="text-lg font-semibold text-primary-950">
                {roleModal.type === 'promotion'
                  ? roleModal.newRole === 'cofounder'
                    ? 'Grant Cofounder Access?'
                    : 'Grant Admin Access?'
                  : roleModal.newRole === 'admin'
                    ? 'Remove Cofounder Access?'
                    : 'Remove Admin Access?'}
              </h3>
            </div>
            <p className="mb-2 text-sm text-primary-950/50">
              {roleModal.type === 'promotion' ? (
                <>You are about to promote <strong className="text-primary-950">{roleModal.email}</strong> to <strong className="text-primary-950 capitalize">{roleModal.newRole}</strong>.</>
              ) : (
                <>You are about to demote <strong className="text-primary-950">{roleModal.email}</strong> to <strong className="text-primary-950 capitalize">{roleModal.newRole}</strong>.</>
              )}
            </p>
            <p className="mb-6 text-sm text-primary-950/50">
              {roleModal.type === 'promotion'
                ? roleModal.newRole === 'cofounder'
                  ? 'This will grant the highest level of access, including the ability to manage admins. Are you sure?'
                  : 'This will give full platform access including user management. Are you sure?'
                : 'This will revoke their elevated privileges. They will no longer be able to manage users or platform settings.'}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setRoleModal(null)}
                className="rounded-lg border border-primary-950/[0.1] px-4 py-2 text-sm font-medium text-primary-950/60 hover:bg-white"
              >
                Cancel
              </button>
              <button
                onClick={confirmRoleChange}
                className={`rounded-lg px-4 py-2 text-sm font-medium text-primary-950 ${
                  roleModal.type === 'promotion'
                    ? roleModal.newRole === 'cofounder'
                      ? 'bg-yellow-600 hover:bg-yellow-700'
                      : 'bg-amber-600 hover:bg-amber-700'
                    : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                {roleModal.type === 'promotion'
                  ? roleModal.newRole === 'cofounder'
                    ? 'Yes, Grant Cofounder'
                    : 'Yes, Grant Admin'
                  : 'Yes, Confirm Demotion'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
