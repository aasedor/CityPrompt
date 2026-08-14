import { afterEach, describe, expect, it } from 'vitest';

import { scrubOAuthCallbackUrl } from './OAuthCallbackPage';

describe('scrubOAuthCallbackUrl', () => {
  afterEach(() => {
    window.history.replaceState(null, '', '/');
  });

  it('removes OAuth credentials from the visible URL immediately', () => {
    window.history.replaceState(
      null,
      '',
      '/oauth/callback?access_token=secret-access&refresh_token=secret-refresh',
    );

    scrubOAuthCallbackUrl();

    expect(window.location.pathname).toBe('/oauth/callback');
    expect(window.location.search).toBe('');
    expect(window.location.href).not.toContain('secret-access');
    expect(window.location.href).not.toContain('secret-refresh');
  });
});
