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
    <div className="flex min-h-screen">
      {/* Left hero panel - desktop only */}
      <div className="hidden w-1/2 flex-col justify-between bg-gradient-primary p-12 lg:flex">
        <div className="flex items-center gap-3">
          <Box className="h-8 w-8 text-accent-300" />
          <span className="text-xl font-bold text-white">SiteForge</span>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">Start building in<br />three dimensions.</h2>
          <p className="mt-4 text-lg text-neutral-300">Create your free account and start designing site plans, generating 3D buildings with AI, and exploring immersive walkthroughs.</p>
        </div>
        <p className="text-sm text-neutral-400">&copy; 2026 SiteForge</p>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-4">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-primary lg:hidden" />

        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <Building2 size={40} className="mx-auto text-primary-400" />
            <h1 className="mt-4 text-2xl font-bold text-white">Create account</h1>
            <p className="mt-1 text-sm text-neutral-400">SiteForge</p>
          </div>

          <form onSubmit={handleSubmit} className="card space-y-4">
            {error && (
              <div className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400">{error}</div>
            )}

            <div>
              <label htmlFor="fullName" className="mb-1 block text-sm font-medium text-neutral-300">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-base w-full"
                placeholder="Optional"
              />
            </div>

            <div>
              <label htmlFor="email" className="mb-1 block text-sm font-medium text-neutral-300">
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

            <div>
              <label htmlFor="password" className="mb-1 block text-sm font-medium text-neutral-300">
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
                  className="input-base w-full pr-10"
                  placeholder="Min 8 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-neutral-500 hover:text-neutral-300"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : 'Create account'}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-neutral-400">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-500 hover:text-primary-400">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
