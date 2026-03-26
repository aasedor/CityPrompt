import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, Loader2, Box } from 'lucide-react';
import { authApi } from '@/services/api';

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
    <div className="flex min-h-screen">
      {/* Left hero panel - desktop only */}
      <div className="hidden w-1/2 flex-col justify-between bg-gradient-primary p-12 lg:flex">
        <div className="flex items-center gap-3">
          <Box className="h-8 w-8 text-accent-300" />
          <span className="text-xl font-bold text-white">City Prompt</span>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">No worries,<br />we've got you.</h2>
          <p className="mt-4 text-lg text-primary-950/60">We'll send a reset link to your email so you can get back to building.</p>
        </div>
        <p className="text-sm text-primary-950/50">&copy; 2026 City Prompt</p>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-4">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-primary lg:hidden" />

        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <Building2 size={40} className="mx-auto text-primary-400" />
            <h1 className="mt-4 text-2xl font-bold text-white">Reset password</h1>
            <p className="mt-1 text-sm text-primary-950/50">
              Enter your email and we'll send you a reset link.
            </p>
          </div>

          {submitted ? (
            <div className="card space-y-4">
              <div className="rounded-lg bg-green-500/10 px-3 py-3 text-sm text-green-400">
                If that email is registered, a password reset link has been sent. Check your inbox.
              </div>
              <Link
                to="/login"
                className="btn-primary w-full justify-center text-center block"
              >
                Back to sign in
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="card space-y-4">
              {error && (
                <div className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-600">{error}</div>
              )}

              <div>
                <label htmlFor="email" className="mb-1 block text-sm font-medium text-primary-950/60">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-base w-full"
                  placeholder="you@example.com"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full justify-center disabled:opacity-50"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : 'Send reset link'}
              </button>
            </form>
          )}

          <p className="mt-4 text-center text-sm text-primary-950/50">
            Remember your password?{' '}
            <Link to="/login" className="font-medium text-primary-500 hover:text-primary-400">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
