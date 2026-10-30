import { expect, it, vi } from 'vitest';
import { createOAuthChallenge, afterOAuthScrub } from './oauthFlow';

it('keeps the verifier in tab storage and returns only its S256 challenge', async () => {
  const { webcrypto } = await vi.importActual<{ webcrypto: Crypto }>('node:crypto');
  // RFC 7636 Appendix B: independently specified verifier/challenge pair.
  const verifierVector = 'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk';
  const bytes = Uint8Array.from(atob(verifierVector.replace(/-/g, '+').replace(/_/g, '/') + '='), char => char.charCodeAt(0));
  const values = new Map<string, string>();
  const storage = { setItem: (key: string, value: string) => { values.set(key, value); } };
  const cryptoApi = { subtle: webcrypto.subtle, getRandomValues: (target: Uint8Array) => { target.set(bytes); return target; } } as unknown as Crypto;
  const challenge = await createOAuthChallenge(storage, cryptoApi);
  const verifier = values.get('cityprompt_oauth_verifier')!;
  expect(verifier).toMatch(/^[A-Za-z0-9_-]{43}$/);
  expect(challenge).toMatch(/^[A-Za-z0-9_-]{43}$/);
  expect(verifier).toBe(verifierVector);
  expect(challenge).toBe('E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM');
  expect(challenge).not.toBe(verifier);
});

it('does not start telemetry until the callback URL is scrubbed', () => {
  const events = new EventTarget();
  const start = vi.fn();
  afterOAuthScrub(start, '/oauth/callback', events);
  expect(start).not.toHaveBeenCalled();
  events.dispatchEvent(new Event('cityprompt:oauth-scrubbed'));
  expect(start).toHaveBeenCalledOnce();
  events.dispatchEvent(new Event('cityprompt:oauth-scrubbed'));
  expect(start).toHaveBeenCalledOnce();
});

it('starts telemetry normally on other pages', () => {
  const start = vi.fn();
  afterOAuthScrub(start, '/projects', new EventTarget());
  expect(start).toHaveBeenCalledOnce();
});
