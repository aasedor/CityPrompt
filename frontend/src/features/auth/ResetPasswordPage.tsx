import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Building2, Eye, EyeOff, Loader2, Box } from 'lucide-react';
import { authApi } from '@/services/api';

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

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
    <div className="flex min-h-screen">
      {/* Left hero panel - desktop only */}
      <div className="hidden w-1/2 flex-col justify-between bg-gradient-primary p-12 lg:flex">
        <div className="flex items-center gap-3">
          <Box className="h-8 w-8 text-accent-300" />
          <span className="text-xl font-bold text-white">SiteForge</span>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">Almost there.<br />Set your new password.</h2>
          <p className="mt-4 text-lg text-primary-950/60">Choose a strong password to secure your account.</p>
        </div>
        <p className="text-sm text-primary-950/50">&copy; 2026 SiteForge</p>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-4">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-primary lg:hidden" />

        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <Building2 size={40} className="mx-auto text-primary-400" />
            <h1 className="mt-4 text-2xl font-bold text-white">Set new password</h1>
            <p className="mt-1 text-sm text-primary-950/50">Enter your new password below.</p>
          </div>

          <form onSubmit={handleSubmit} className="card space-y-4">
            {error && (
              <div className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-600">{error}</div>
            )}

            <div>
              <label htmlFor="newPassword" className="mb-1 block text-sm font-medium text-primary-950/60">
                New password
              </label>
              <div className="relative">
                <input
                  id="newPassword"
                  type={showNew ? 'text' : 'password'}
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="input-base w-full pr-10"
                  placeholder="Min 8 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowNew((v) => !v)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-primary-950/40 hover:text-primary-950/60"
                  tabIndex={-1}
                >
                  {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="mb-1 block text-sm font-medium text-primary-950/60">
                Confirm password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirm ? 'text' : 'password'}
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-base w-full pr-10"
                  placeholder="Re-enter password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm((v) => !v)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-primary-950/40 hover:text-primary-950/60"
                  tabIndex={-1}
                >
                  {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : 'Reset password'}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-primary-950/50">
            <Link to="/login" className="font-medium text-primary-500 hover:text-primary-400">
              Back to sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
