import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';
import {
  AuthPageShell,
  authErrorClassName,
  authFormClassName,
  authInputClassName,
  authLabelClassName,
  authSubmitClassName,
} from './AuthPageShell';

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
    <AuthPageShell
      eyebrow="New password"
      title="Set password"
      description="Choose a new password and jump back into your workspace."
      sideTitle="Almost there."
      sideDescription="Secure the account, then get back to projects, saved generations, and development visuals."
    >
      <form onSubmit={handleSubmit} className={authFormClassName}>
        {error && <div className={authErrorClassName}>{error}</div>}

        <div>
          <label htmlFor="newPassword" className={authLabelClassName}>
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
              className={`${authInputClassName} pr-10`}
              placeholder="Min 8 characters"
            />
            <button
              type="button"
              onClick={() => setShowNew((v) => !v)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#151515]/45 hover:text-[#151515]"
              tabIndex={-1}
            >
              {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div>
          <label htmlFor="confirmPassword" className={authLabelClassName}>
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
              className={`${authInputClassName} pr-10`}
              placeholder="Re-enter password"
            />
            <button
              type="button"
              onClick={() => setShowConfirm((v) => !v)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#151515]/45 hover:text-[#151515]"
              tabIndex={-1}
            >
              {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <button type="submit" disabled={loading} className={authSubmitClassName}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : 'Reset password'}
        </button>
      </form>

      <p className="mt-5 text-center text-sm font-semibold text-[#151515]/60">
        <Link to="/login" className="font-black text-[#0aa6a6] hover:text-[#151515]">
          Back to sign in
        </Link>
      </p>
    </AuthPageShell>
  );
}
