import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';
import {
  AuthPageShell,
  authErrorClassName,
  authFormClassName,
  authInputClassName,
  authLabelClassName,
  authSubmitClassName,
  authSuccessClassName,
} from './AuthPageShell';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authApi.forgotPassword(email);
      setSubmitted(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthPageShell
      eyebrow="Reset access"
      title="Reset password"
      description="Enter your email and we will send a reset link if the account exists."
      sideTitle="Back to the board."
      sideDescription="A reset flow that still feels like City Prompt: direct, visual, and built around keeping your planning work moving."
    >
      {submitted ? (
        <div className={authFormClassName}>
          <div className={authSuccessClassName}>
            If that email is registered, a password reset link has been sent. Check your inbox.
          </div>
          <Link to="/login" className={authSubmitClassName}>
            Back to sign in
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className={authFormClassName}>
          {error && <div className={authErrorClassName}>{error}</div>}

          <div>
            <label htmlFor="email" className={authLabelClassName}>
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={authInputClassName}
              placeholder="you@example.com"
            />
          </div>

          <button type="submit" disabled={loading} className={authSubmitClassName}>
            {loading ? <Loader2 size={16} className="animate-spin" /> : 'Send reset link'}
          </button>
        </form>
      )}

      <p className="mt-5 text-center text-sm font-semibold text-[#151515]/60">
        Remember your password?{' '}
        <Link to="/login" className="font-black text-[#0aa6a6] hover:text-[#151515]">
          Sign in
        </Link>
      </p>
    </AuthPageShell>
  );
}
