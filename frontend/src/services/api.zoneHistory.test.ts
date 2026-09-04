import { afterEach, describe, expect, it } from 'vitest';
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { api, siteZonesApi } from './api';

const originalAdapter = api.defaults.adapter;
afterEach(() => { api.defaults.adapter = originalAdapter; });

describe('request-scoped undo history', () => {
  it.each(['create', 'update', 'delete'] as const)('pending project A %s cannot suppress project B history', async (operation) => {
    const requests: InternalAxiosRequestConfig[] = [];
    let finishFirst!: () => void;
    api.defaults.adapter = (config) => {
      requests.push(config);
      const response: AxiosResponse = { data: { id: 'saved', updated_at: 'r2' }, status: 200, statusText: 'OK', headers: {}, config };
      if (requests.length === 1) return new Promise((resolve) => { finishFirst = () => resolve(response); });
      return Promise.resolve(response);
    };
    const request = (project: string, skipHistory = false) => {
      const options = skipHistory ? { skipHistory: true } : undefined;
      if (operation === 'create') return siteZonesApi.create(project, {
        zone_type: 'green_space', coordinates: [[0, 0], [1, 0], [1, 1]], color: '#008800',
      }, options);
      if (operation === 'update') return siteZonesApi.update(project, { name: 'Changed', expected_updated_at: 'r1' }, options);
      return siteZonesApi.delete(project, 'r1', options);
    };
    // Queue both before Axios executes its async interceptors. B's authored
    // request must retain history while A's system request remains unresolved.
    const first = request('project-a', true);
    await request('project-b');
    expect(requests[0].headers.get('X-Skip-History')).toBe('1');
    expect(requests[1].headers.has('X-Skip-History')).toBe(false);
    if (operation === 'delete') expect(requests[1].params.expected_updated_at).toBe('r1');
    // A fresh system action in B keeps its own header after A finishes.
    await request('project-b', true);
    finishFirst();
    await first;
    expect(requests[2].headers.get('X-Skip-History')).toBe('1');
  });
});
