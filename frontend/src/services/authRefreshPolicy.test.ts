import { describe, expect, it } from 'vitest';
import { shouldAttemptTokenRefresh } from './authRefreshPolicy';

describe('shouldAttemptTokenRefresh', () => {
  it('renews an expired access token during session bootstrap', () => {
    expect(shouldAttemptTokenRefresh(401, '/api/v1/auth/me', false)).toBe(true);
  });

  it.each([
    '/api/v1/auth/login',
    '/api/v1/auth/register',
    '/api/v1/auth/refresh',
    '/api/v1/auth/forgot-password',
    '/api/v1/auth/reset-password',
    '/api/v1/auth/oauth/google',
  ])('does not recurse on credential endpoint %s', (url) => {
    expect(shouldAttemptTokenRefresh(401, url, false)).toBe(false);
  });

  it('does not retry non-401s or a request already retried', () => {
    expect(shouldAttemptTokenRefresh(500, '/api/v1/projects', false)).toBe(false);
    expect(shouldAttemptTokenRefresh(401, '/api/v1/projects', true)).toBe(false);
  });
});
