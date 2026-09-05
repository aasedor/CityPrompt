import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { resetSessionState } from '@/utils/sessionReset';
import { safeReturnTo } from './returnTo';

export function scrubOAuthCallbackUrl(): void {
  window.history.replaceState(window.history.state, '', '/oauth/callback');
}

/**
 * Handles the OAuth2 redirect callback.
 * The backend redirects here with access_token and refresh_token as query params.
 * This page immediately removes them from the visible URL, stores them, fetches
 * the user profile, and then navigates to the app.
 */
export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const { setUser } = useAuthStore();

  useEffect(() => {
    const oauthError = searchParams.get('oauth_error')
      || searchParams.get('error_description')
      || searchParams.get('error');

    if (oauthError) {
      toast.error(`OAuth login failed: ${oauthError}`);
      navigate('/login', { replace: true });
      return;
    }

    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');

    if (!accessToken || !refreshToken) {
      toast.error('OAuth login failed: missing tokens');
      navigate('/login', { replace: true });
      return;
    }

    // The callback tokens are credentials. Remove them from the address bar
    // and browser history before performing any asynchronous work so they are
    // not left visible in screenshots or copied URLs.
    scrubOAuthCallbackUrl();

    // Store tokens
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);

    // Fetch user profile and redirect
    authApi
      .me()
      .then((user) => {
        resetSessionState(queryClient);
        setUser(user);
        toast.success(`Welcome, ${user.full_name || user.email}!`);
        const returnTo = localStorage.getItem('oauth_return_to');
        localStorage.removeItem('oauth_return_to');
        navigate(safeReturnTo(returnTo), { replace: true });
      })
      .catch(() => {
        toast.error('Failed to load user profile after OAuth login');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/login', { replace: true });
      });
  }, [searchParams, navigate, queryClient, setUser]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <Loader2 size={32} className="mx-auto animate-spin text-primary-400" />
        <p className="mt-4 text-sm text-neutral-400">Completing sign in...</p>
      </div>
    </div>
  );
}
