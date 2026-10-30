import { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { afterEach, expect, it, vi } from 'vitest';
import { api } from './api';

const originalAdapter = api.defaults.adapter;

afterEach(() => {
  api.defaults.adapter = originalAdapter;
  localStorage.clear();
});

function denied(config: InternalAxiosRequestConfig) {
  return new AxiosError('Expired session', 'ERR_BAD_REQUEST', config, undefined, {
    data: {}, status: 401, statusText: 'Unauthorized', headers: {}, config,
  });
}

it('shares one refresh rotation across simultaneous expired requests', async () => {
  localStorage.setItem('access_token', 'expired-access');
  localStorage.setItem('refresh_token', 'single-use-refresh');
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  let refreshCalls = 0;
  let consumed = false;
  api.defaults.adapter = async config => {
    if (config.url?.endsWith('/auth/refresh')) {
      refreshCalls += 1;
      await gate;
      if (consumed) throw denied(config);
      consumed = true;
      return { data: { access_token: 'fresh-access', refresh_token: 'rotated-refresh' }, status: 200, statusText: 'OK', headers: {}, config };
    }
    if (config.headers.Authorization !== 'Bearer fresh-access') throw denied(config);
    return { data: { project: 'student-project' }, status: 200, statusText: 'OK', headers: {}, config };
  };
  const responses = Promise.allSettled(Array.from({ length: 6 }, () => api.get('/api/v1/projects')));
  await vi.waitFor(() => expect(refreshCalls).toBeGreaterThan(0));
  release();
  const outcomes = await responses;
  expect(outcomes.filter(result => result.status === 'fulfilled')).toHaveLength(6);
  expect(refreshCalls).toBe(1);
  expect(localStorage.getItem('refresh_token')).toBe('rotated-refresh');
});

it('does not overwrite a new sign-in when an old refresh finishes late', async () => {
  localStorage.setItem('access_token', 'expired-access');
  localStorage.setItem('refresh_token', 'old-account-refresh');
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  let started = false;
  api.defaults.adapter = async config => {
    if (config.url?.endsWith('/auth/refresh')) {
      started = true;
      await gate;
      return { data: { access_token: 'old-account-access', refresh_token: 'old-account-rotated' }, status: 200, statusText: 'OK', headers: {}, config };
    }
    if (config.headers.Authorization === 'Bearer expired-access') throw denied(config);
    return { data: {}, status: 200, statusText: 'OK', headers: {}, config };
  };
  const pending = Promise.allSettled([api.get('/api/v1/projects')]);
  await vi.waitFor(() => expect(started).toBe(true));
  localStorage.setItem('access_token', 'new-account-access');
  localStorage.setItem('refresh_token', 'new-account-refresh');
  release();
  const [outcome] = await pending;
  expect(outcome.status).toBe('rejected');
  expect(localStorage.getItem('access_token')).toBe('new-account-access');
  expect(localStorage.getItem('refresh_token')).toBe('new-account-refresh');
});
