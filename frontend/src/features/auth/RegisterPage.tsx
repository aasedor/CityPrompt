import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Building2, Eye, EyeOff, Loader2, Box } from 'lucide-react';
import { authApi } from '@/services/api';

export function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authApi.register(email, password, fullName || undefined);
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-accent-50">
      {/* Left hero panel - desktop only */}
      <div className="hidden w-1/2 flex-col justify-between bg-primary-950 p-12 lg:flex">
        <div className="flex items-center gap-3">
          <img src="/images/city-prompt-logo.png" alt="City Prompt" className="h-10 w-10" />
          <span className="text-xl font-bold text-white">City Prompt</span>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">Start building in<br />three dimensions.</h2>
          <p className="mt-4 text-lg text-white/50">Create your free account and start designing site plans, generating 3D buildings with AI, and exploring immersive walkthroughs.</p>
        </div>
        <p className="text-sm text-white/30">&copy; 2026 City Prompt</p>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <Building2 size={40} className="mx-auto text-primary-400" />
            <h1 className="mt-4 text-2xl font-bold text-primary-950">Create account</h1>
            <p className="mt-1 text-sm text-primary-950/40">City Prompt</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-primary-950/[0.06] bg-white p-6 shadow-sm">
            {error && (
              <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>
            )}

            <div>
              <label htmlFor="fullName" className="mb-1 block text-sm font-medium text-primary-950/70">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-xl border border-primary-950/[0.1] bg-accent-50 px-3.5 py-2.5 text-sm text-primary-950 placeholder:text-primary-950/30 transition-all focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-400/20"
                placeholder="Optional"
              />
            </div>

            <div>
              <label htmlFor="email" className="mb-1 block text-sm font-medium text-primary-950/70">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-primary-950/[0.1] bg-accent-50 px-3.5 py-2.5 text-sm text-primary-950 placeholder:text-primary-950/30 transition-all focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-400/20"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1 block text-sm font-medium text-primary-950/70">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-primary-950/[0.1] bg-accent-50 px-3.5 py-2.5 pr-10 text-sm text-primary-950 placeholder:text-primary-950/30 transition-all focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-400/20"
                  placeholder="Min 8 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-primary-950/30 hover:text-primary-950/60"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full justify-center rounded-xl bg-primary-400 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary-400/20 transition-all hover:bg-primary-300 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-primary-400/30 active:scale-[0.97] disabled:opacity-50 inline-flex items-center"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : 'Create account'}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-primary-950/40">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-400 hover:text-primary-500">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
