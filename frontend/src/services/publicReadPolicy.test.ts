import { expect, it } from 'vitest';
import { isPublicReadRequest } from './authRefreshPolicy';
it('keeps public links independent from cached account tokens but requires login to accept an invitation', () => {
  expect(isPublicReadRequest('/api/v1/shares/shared/panel')).toBe(true);
  expect(isPublicReadRequest('/api/v1/shares/invitations/invite')).toBe(true);
  expect(isPublicReadRequest('/api/v1/render/projects/p/renders', 'get', { share_token: 'panel' })).toBe(true);
  expect(isPublicReadRequest('/api/v1/shares/invitations/invite/accept', 'post')).toBe(false);
  expect(isPublicReadRequest('/api/v1/site-zones/zone', 'put', { share_token: 'panel' })).toBe(false);
  expect(isPublicReadRequest('/api/v1/projects/p', 'get')).toBe(false);
});
