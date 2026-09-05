import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';
import { safeReturnTo } from './returnTo';
import {
  AuthPageShell,
  authErrorClassName,
  authFormClassName,
  authInputClassName,
  authLabelClassName,
  authSubmitClassName,
} from './AuthPageShell';

export function RegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const returnTo = safeReturnTo(new URLSearchParams(location.search).get('returnTo'));
  const loginUrl = `/login?returnTo=${encodeURIComponent(returnTo)}`;
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
      navigate(loginUrl);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthPageShell
      eyebrow="Start building"
      title="Create account"
      description="Make a workspace for projects, saved renders, and visual planning studies."
      sideTitle="Make a place."
      sideDescription="Create projects from real addresses, shape zones on the map, and turn planning choices into finished render directions."
    >
      <form onSubmit={handleSubmit} className={authFormClassName}>
        {error && <div className={authErrorClassName}>{error}</div>}

        <div>
          <label htmlFor="fullName" className={authLabelClassName}>
            Full name
          </label>
          <input
            id="fullName"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className={authInputClassName}
            placeholder="Optional"
          />
        </div>

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
          <label htmlFor="password" className={authLabelClassName}>
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
          {loading ? <Loader2 size={16} className="animate-spin" /> : 'Create account'}
        </button>
      </form>

      <p className="mt-5 text-center text-sm font-semibold text-[#151515]/60">
        Already have an account?{' '}
        <Link to={loginUrl} className="font-black text-[#0aa6a6] hover:text-[#151515]">
          Sign in
        </Link>
      </p>
    </AuthPageShell>
  );
}
