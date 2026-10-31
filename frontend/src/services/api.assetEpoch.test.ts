import { afterEach, expect, it } from 'vitest';
import { api, resolveApiFileUrl } from './api';
import { assetAccountIdentity } from './assetAccess';

const originalAdapter = api.defaults.adapter;
afterEach(() => {
  api.defaults.adapter = originalAdapter;
  localStorage.clear();
});

function accessToken(version: number, expires: number) {
  return `header.${btoa(JSON.stringify({ type: 'access', sub: 'student', ver: version, exp: expires }))}.signature`;
}

it('reuses asset tickets during normal rotation but replaces them after the same user recovers their password', async () => {
  const project = '8a2f05d7-9ceb-4815-8204-3856279f1ad2';
  const image = `/api/v1/files/projects/${project}/renders/private.png`;
  let epoch = 0;
  let tickets = 0;
  localStorage.setItem('access_token', accessToken(0, 1));
  api.defaults.adapter = async config => {
    let data: unknown = { image_url: image };
    if (config.url?.endsWith('/asset-ticket')) {
      tickets += 1;
      data = { asset_ticket: epoch === 0 ? 'old-epoch-ticket' : 'recovered-ticket', expires_in: 900 };
    }
    return { data, status: 200, statusText: 'OK', headers: {}, config };
  };
  const first = (await api.get(`/api/v1/projects/${project}/scene`)).data.image_url as string;
  expect(first).toContain('asset_ticket=old-epoch-ticket');
  localStorage.setItem('access_token', accessToken(0, 2));
  expect((await api.get(`/api/v1/projects/${project}/scene`)).data.image_url).toContain('asset_ticket=old-epoch-ticket');
  expect(tickets).toBe(1);
  epoch = 1;
  localStorage.setItem('access_token', accessToken(1, 3));
  expect(resolveApiFileUrl(first)).not.toContain('old-epoch-ticket');
  expect((await api.get(`/api/v1/projects/${project}/scene`)).data.image_url).toContain('asset_ticket=recovered-ticket');
  expect(tickets).toBe(2);
  // Durable image recovery still belongs to the user across credential epochs.
  expect(assetAccountIdentity(accessToken(0, 1))).toBe('student');
  expect(assetAccountIdentity(accessToken(1, 3))).toBe('student');
});
