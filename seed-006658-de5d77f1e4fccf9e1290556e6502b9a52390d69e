const NON_REFRESHABLE_AUTH_PATHS = [
  '/auth/login',
  '/auth/register',
  '/auth/refresh',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/oauth/',
];

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
