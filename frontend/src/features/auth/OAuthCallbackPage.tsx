import { useEffect, useRef } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { resetSessionState } from '@/utils/sessionReset';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { safeReturnTo } from './returnTo';
import { OAUTH_SCRUBBED, OAUTH_VERIFIER_KEY } from './oauthFlow';

export function scrubOAuthCallbackUrl(): void {
  window.history.replaceState(window.history.state, '', '/oauth/callback');
  window.dispatchEvent(new Event(OAUTH_SCRUBBED));
}

/**
 * Handles the OAuth2 redirect callback.
 * The URL carries only a single-use code. Tokens arrive in a POST response
 * after proof from this tab, and never serve as URL fallback credentials.
 */
export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const started = useRef(false);
  const active = useRef(true);
  const { setUser } = useAuthStore();

  useEffect(() => {
    active.current = true;
    return () => { active.current = false; };
  }, []);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    scrubOAuthCallbackUrl();
    const oauthError = searchParams.get('oauth_error')
      || searchParams.get('error_description')
      || searchParams.get('error');

    if (oauthError) {
      toast.error(`OAuth login failed: ${oauthError}`);
      navigate('/login', { replace: true });
      return;
    }

    const code = searchParams.get('code');
    if (!code || searchParams.has('access_token') || searchParams.has('refresh_token') || location.hash) {
      toast.error('This sign-in expired. Refresh the sign-in page and try again.');
      navigate('/login', { replace: true });
      return;
    }

    const failSignIn = (message: string) => {
      if (!active.current) return;
      // A partial credential write must not leave the UI signed in. Storage
      // removal can itself be blocked, so always finish the in-memory reset.
      for (const key of ['access_token', 'refresh_token']) {
        try { localStorage.removeItem(key); } catch { /* storage unavailable */ }
      }
      resetSessionState(queryClient);
      setUser(null);
      toast.error(message);
      navigate('/login', { replace: true });
    };

    let verifier: string | null;
    try {
      verifier = sessionStorage.getItem(OAUTH_VERIFIER_KEY);
      sessionStorage.removeItem(OAUTH_VERIFIER_KEY);
      if (!verifier) throw new Error('Missing browser proof');
    } catch {
      failSignIn('Sign-in expired or browser storage is unavailable. Start sign-in again.');
      return;
    }

    authApi
      .exchangeOAuthCode(code, verifier)
      .then(({ user, access_token, refresh_token }) => {
        if (!active.current) return;
        try {
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
        } catch {
          failSignIn('Could not save your sign-in session. Enable browser storage or free up space, then try again.');
          return;
        }
        resetSessionState(queryClient);
        setUser(user);
        toast.success(`Welcome, ${user.full_name || user.email}!`);
        const returnTo = readBrowserPreference('oauth_return_to');
        writeBrowserPreference('oauth_return_to', null);
        navigate(safeReturnTo(returnTo), { replace: true });
      })
      .catch(() => {
        failSignIn('Sign-in expired or could not be completed. Start sign-in again.');
      });
  }, [searchParams, location.hash, navigate, queryClient, setUser]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <Loader2 size={32} className="mx-auto animate-spin text-primary-400" />
        <p className="mt-4 text-sm text-neutral-400">Completing sign in...</p>
      </div>
    </div>
  );
}
