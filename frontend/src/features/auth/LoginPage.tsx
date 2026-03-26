import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Building2, Eye, EyeOff, Loader2, Box } from 'lucide-react';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { OAuthButtons } from './OAuthButtons';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser } = useAuthStore();
  const from = (location.state as any)?.from?.pathname || '/projects';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await authApi.login(email, password);
      setUser(result.user);
      toast.success(`Welcome back, ${result.user.full_name || result.user.email}!`);
      navigate(from, { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (typeof detail === 'string' && detail.trim()) {
        setError(detail);
      } else if (err?.code === 'ERR_NETWORK' || !err?.response) {
        setError('Unable to reach the API server. Make sure backend is running on http://localhost:8000.');
      } else {
        setError('Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-accent-50">
      {/* Left hero panel - desktop only */}
      <div className="hidden w-1/2 flex-col justify-between bg-primary-950 p-12 lg:flex">
        <div className="flex items-center gap-3">
          <Box className="h-8 w-8 text-coral-500" />
          <span className="text-xl font-bold text-white">City Prompt</span>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">Design, plan, and visualize<br />in three dimensions.</h2>
          <p className="mt-4 text-lg text-white/50">Create site plans on satellite maps, generate AI-powered buildings, and explore immersive 3D walkthroughs — all from your browser.</p>
        </div>
        <p className="text-sm text-white/30">&copy; 2026 City Prompt</p>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <Building2 size={40} className="mx-auto text-primary-400" />
            <h1 className="mt-4 text-2xl font-bold text-primary-950">Sign in</h1>
            <p className="mt-1 text-sm text-primary-950/40">City Prompt</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-primary-950/[0.06] bg-white p-6 shadow-sm">
            {error && (
              <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>
            )}

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
              <div className="mb-1 flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-medium text-primary-950/70">
                  Password
                </label>
                <Link to="/forgot-password" tabIndex={-1} className="text-xs font-medium text-primary-400 hover:text-primary-500">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
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
              {loading ? <Loader2 size={16} className="animate-spin" /> : 'Sign in'}
            </button>

            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-primary-950/[0.06]" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-primary-950/30">or</span>
              </div>
            </div>

            <OAuthButtons />
          </form>

          <p className="mt-4 text-center text-sm text-primary-950/40">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-primary-400 hover:text-primary-500">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
