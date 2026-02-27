import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Building2, Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!token) {
      setError('Missing reset token. Please use the link from your email.');
      return;
    }

    setLoading(true);

    try {
      await authApi.resetPassword(token, newPassword);
      toast.success('Password reset successfully! Please sign in.');
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password. The link may have expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <Building2 size={40} className="mx-auto text-primary-600" />
          <h1 className="mt-4 text-2xl font-bold text-gray-900">Set new password</h1>
          <p className="mt-1 text-sm text-gray-500">Enter your new password below.</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>
          )}

          <div>
            <label htmlFor="newPassword" className="mb-1 block text-sm font-medium text-gray-700">
              New password
            </label>
            <input
              id="newPassword"
              type="password"
              required
              minLength={8}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="Min 8 characters"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="mb-1 block text-sm font-medium text-gray-700">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              minLength={8}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="Re-enter password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : 'Reset password'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
