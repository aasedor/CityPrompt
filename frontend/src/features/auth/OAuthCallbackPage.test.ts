import { afterEach, describe, expect, it, vi } from 'vitest';

import { scrubOAuthCallbackUrl } from './OAuthCallbackPage';

describe('scrubOAuthCallbackUrl', () => {
  afterEach(() => {
    window.history.replaceState(null, '', '/');
  });

  it.each(['?access_token=secret-access&refresh_token=secret-refresh', '#access_token=secret-access&refresh_token=secret-refresh'])('scrubs %s before releasing startup telemetry', (suffix) => {
    window.history.replaceState(
      null,
      '',
      '/oauth/callback' + suffix,
    );
    const telemetry = vi.fn(() => {
      expect(window.location.search).toBe('');
      expect(window.location.hash).toBe('');
    });
    window.addEventListener('cityprompt:oauth-scrubbed', telemetry, { once: true });

    scrubOAuthCallbackUrl();

    expect(window.location.pathname).toBe('/oauth/callback');
    expect(window.location.search).toBe('');
    expect(window.location.href).not.toContain('secret-access');
    expect(window.location.href).not.toContain('secret-refresh');
    expect(telemetry).toHaveBeenCalledOnce();
  });
});
