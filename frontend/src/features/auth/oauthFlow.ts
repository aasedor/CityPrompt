export const OAUTH_VERIFIER_KEY = 'cityprompt_oauth_verifier';
export const OAUTH_SCRUBBED = 'cityprompt:oauth-scrubbed';

export async function createOAuthChallenge(storage: Pick<Storage, 'setItem'> = sessionStorage, cryptoApi = crypto): Promise<string> {
  const encode = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const verifier = encode(cryptoApi.getRandomValues(new Uint8Array(32)));
  const challenge = encode(new Uint8Array(await cryptoApi.subtle.digest('SHA-256', new TextEncoder().encode(verifier))));
  storage.setItem(OAUTH_VERIFIER_KEY, verifier);
  return challenge;
}

/** Prevent initial tracing/replay from retaining a pre-scrub callback URL. */
export function afterOAuthScrub(start: () => void, pathname = window.location.pathname, events: EventTarget = window): void {
  if (pathname === '/oauth/callback') events.addEventListener(OAUTH_SCRUBBED, start, { once: true });
  else start();
}
