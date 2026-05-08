import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { OAuthButtons } from './OAuthButtons';
import {
  AuthPageShell,
  authErrorClassName,
  authFormClassName,
  authInputClassName,
  authLabelClassName,
  authSubmitClassName,
} from './AuthPageShell';

interface LoginFormProps {
  returnTo?: string;
  showSignupPrompt?: boolean;
}

export function LoginForm({ returnTo = '/projects', showSignupPrompt = true }: LoginFormProps) {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
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
      navigate(returnTo, { replace: true });
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
    <>
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

        <div>
          <div className="mb-1 flex items-center justify-between">
            <label htmlFor="password" className={authLabelClassName}>
              Password
            </label>
            <Link to="/forgot-password" tabIndex={-1} className="text-xs font-black uppercase text-[#0aa6a6] hover:text-[#151515]">
              Forgot?
            </Link>
          </div>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`${authInputClassName} pr-10`}
              placeholder="Min 8 characters"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#151515]/45 hover:text-[#151515]"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <button type="submit" disabled={loading} className={authSubmitClassName}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : 'Sign in'}
        </button>

        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t-2 border-[#151515]" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-3 font-black text-[#151515]/45">or</span>
          </div>
        </div>

        <OAuthButtons returnTo={returnTo} />
      </form>

      {showSignupPrompt && (
        <p className="mt-5 text-center text-sm font-semibold text-[#151515]/60">
          Don't have an account?{' '}
          <Link to="/register" className="font-black text-[#0aa6a6] hover:text-[#151515]">
            Sign up
          </Link>
        </p>
      )}
    </>
  );
}

export function LoginPage() {
  const location = useLocation();
  const fromLocation = (location.state as any)?.from;
  const from = fromLocation
    ? `${fromLocation.pathname || '/projects'}${fromLocation.search || ''}${fromLocation.hash || ''}`
    : '/projects';

  return (
    <AuthPageShell
      eyebrow="Welcome back"
      title="Sign in"
      description="Get back to your projects, saved images, and render experiments."
      sideTitle="Plan visual futures."
      sideDescription="Turn a real address into mapped zones, style systems, saved generations, and AI renders that make early development ideas feel tangible."
    >
      <LoginForm returnTo={from} />
    </AuthPageShell>
  );
}
