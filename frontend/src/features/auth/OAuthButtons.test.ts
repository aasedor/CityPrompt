import { describe, expect, it } from 'vitest';

import { readOAuthAuthorizationUrl } from './OAuthButtons';

function responseStub(options: {
  ok: boolean;
  status: number;
  body: string;
}): Response {
  return {
    ok: options.ok,
    status: options.status,
    text: async () => options.body,
  } as Response;
}

describe('readOAuthAuthorizationUrl', () => {
  it('returns a valid provider URL', async () => {
    const url = await readOAuthAuthorizationUrl(responseStub({
      ok: true,
      status: 200,
      body: JSON.stringify({ authorization_url: 'https://accounts.google.com/o/oauth2/v2/auth' }),
    }), 'google');

    expect(url).toBe('https://accounts.google.com/o/oauth2/v2/auth');
  });

  it('explains an empty proxy error instead of throwing a JSON parse error', async () => {
    await expect(readOAuthAuthorizationUrl(responseStub({
      ok: false,
      status: 500,
      body: '',
    }), 'google')).rejects.toThrow('empty response (HTTP 500)');
  });

  it('preserves a structured backend error', async () => {
    await expect(readOAuthAuthorizationUrl(responseStub({
      ok: false,
      status: 501,
      body: JSON.stringify({ detail: 'Google OAuth is not configured' }),
    }), 'google')).rejects.toThrow('Google OAuth is not configured');
  });
});
