const NON_REFRESHABLE_AUTH_PATHS = [
  '/auth/login',
  '/auth/register',
  '/auth/refresh',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/oauth/',
];

/** A presentation link works independently of any account cached in this tab. */
export function isPublicReadRequest(url?: string, method?: string, params?: Record<string, unknown>): boolean {
  if ((method || 'get').toLowerCase() !== 'get' || !url) return false;
  const parsed = new URL(url, 'https://local.invalid');
  const path = parsed.pathname;
  return /^\/api\/v1\/shares\/shared\/[^/]+$/.test(path)
    || /^\/api\/v1\/shares\/invitations\/[^/]+$/.test(path)
    || Boolean(params?.share_token || parsed.searchParams.get('share_token'));
}

/** `/auth/me` is intentionally refreshable: it is the session bootstrap
 * request after a page reload. Only credential and refresh-loop endpoints are
 * excluded from automatic token renewal. */
export function shouldAttemptTokenRefresh(
  status: number | undefined,
  url: string | undefined,
  alreadyRetried: boolean | undefined,
): boolean {
  if (status !== 401 || alreadyRetried || !url) return false;
  const path = String(url ?? '').toLowerCase();
  return !NON_REFRESHABLE_AUTH_PATHS.some((blocked) => path.includes(blocked));
}
