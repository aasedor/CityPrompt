import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const API_BASE = import.meta.env.VITE_API_URL || '';

interface OAuthButtonsProps {
  returnTo?: string;
}

interface OAuthStartPayload {
  authorization_url?: unknown;
  detail?: unknown;
}

export async function readOAuthAuthorizationUrl(
  response: Response,
  provider: 'google' | 'microsoft',
): Promise<string> {
  const body = await response.text();
  let payload: OAuthStartPayload = {};
  if (body.trim()) {
    try {
      payload = JSON.parse(body) as OAuthStartPayload;
    } catch {
      throw new Error(
        `The login API returned an invalid response (HTTP ${response.status}). Check the API connection and try again.`,
      );
    }
  }

  if (!response.ok) {
    const detail = typeof payload.detail === 'string' ? payload.detail : null;
    throw new Error(
      detail
      || `The login API returned an empty response (HTTP ${response.status}). Check the API connection and try again.`,
    );
  }
  if (typeof payload.authorization_url !== 'string' || !payload.authorization_url) {
    throw new Error(`The login API did not return a ${provider} authorization URL.`);
  }
  return payload.authorization_url;
}

export function OAuthButtons({ returnTo = '/projects' }: OAuthButtonsProps) {
  const [loadingProvider, setLoadingProvider] = useState<string | null>(null);

  const handleOAuth = async (provider: 'google' | 'microsoft') => {
    setLoadingProvider(provider);
    try {
      localStorage.setItem('oauth_return_to', returnTo);
      const url = new URL(`${API_BASE}/api/v1/auth/oauth/${provider}`, API_BASE || window.location.origin);
      url.searchParams.set('frontend_origin', window.location.origin);

      const response = await fetch(url.toString());
      const authorizationUrl = await readOAuthAuthorizationUrl(response, provider);

      // Redirect browser to the OAuth provider's authorization page.
      window.location.href = authorizationUrl;
    } catch (error) {
      const message = error instanceof Error ? error.message : `Failed to initiate ${provider} login`;
      toast.error(
        message === 'Failed to fetch'
          ? `Could not reach the API at ${API_BASE}. Start the backend and try again.`
          : message,
      );
      setLoadingProvider(null);
    }
  };

  return (
    <div className="space-y-3">
      <button
        type="button"
        disabled={loadingProvider !== null}
        onClick={() => handleOAuth('google')}
        className="flex w-full items-center justify-center gap-3 rounded-full border-2 border-[#151515] bg-white px-3 py-2.5 text-sm font-black text-[#151515] shadow-[4px_4px_0_0_#151515] transition hover:bg-[#c9ff3d] focus:outline-none focus:ring-2 focus:ring-[#c9ff3d] disabled:opacity-50"
      >
        {loadingProvider === 'google' ? (
          <Loader2 size={18} className="animate-spin" />
        ) : (
          <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
            <path
              fill="#EA4335"
              d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
            />
            <path
              fill="#4285F4"
              d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
            />
            <path
              fill="#FBBC05"
              d="M10.53 28.59a14.5 14.5 0 0 1 0-9.18l-7.98-6.19a24.04 24.04 0 0 0 0 21.56l7.98-6.19z"
            />
            <path
              fill="#34A853"
              d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
            />
            <path fill="none" d="M0 0h48v48H0z" />
          </svg>
        )}
        Continue with Google
      </button>
    </div>
  );
}
