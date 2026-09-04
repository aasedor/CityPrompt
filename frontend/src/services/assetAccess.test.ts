import { describe, expect, it, vi } from 'vitest';
import { assetAccountIdentity, createAssetAccess } from './assetAccess';

function token(subject: string, version = 1, type = 'access') {
  return `header.${btoa(JSON.stringify({ sub: subject, type, exp: version })).replace(/=/g, '')}.signature-${version}`;
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function setup() {
  const projectTicket = vi.fn().mockResolvedValue({ asset_ticket: 'project-read', expires_in: 900 });
  const fileTicket = vi.fn().mockResolvedValue({ file_ticket: 'one-file', expires_in: 900 });
  let session: string | null = token('account-a');
  const access = createAssetAccess({ baseUrl: '', origin: () => 'https://cityprompt.ca', session: () => assetAccountIdentity(session), projectTicket, fileTicket });
  return { access, projectTicket, fileTicket, getToken: () => session!,
    setToken: (next: string | null) => { session = next; },
    logout: () => { session = null; access.clear(); },
  };
}
describe('scoped media downloads', () => {
  it('prepares one ticket for multiple project assets without putting the login token in URLs', async () => {
    const { access, projectTicket, getToken } = setup();
    const result = await access.prepare({ images: ['/api/v1/files/projects/p/renders/a.png', '/api/v1/files/projects/p/renders/b.png'] });
    expect(projectTicket).toHaveBeenCalledTimes(1);
    expect(result.images.every((url) => url.includes('asset_ticket=project-read'))).toBe(true);
    expect(JSON.stringify(result)).not.toContain(getToken());
  });
  it('does not send credentials to third-party URLs that resemble the file API', async () => {
    const { access, projectTicket, fileTicket } = setup();
    const remote = 'https://outside.example/api/v1/files/projects/p/secret.png';
    expect(await access.prepare({ image_url: remote })).toEqual({ image_url: remote });
    expect(access.resolve(remote, { shareToken: 'public-secret' })).toBe(remote);
    expect(projectTicket).not.toHaveBeenCalled(); expect(fileTicket).not.toHaveBeenCalled();
  });
  it('uses exact-file tickets for a private library and public tokens for shared presentations', async () => {
    const { access, fileTicket, projectTicket } = setup();
    expect((await access.prepare({ model_url: '/api/v1/files/library/a/model.glb' })).model_url).toContain('file_ticket=one-file');
    expect(fileTicket).toHaveBeenCalledWith('library/a/model.glb');
    const shared = await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' }, { projectId: 'p', shareToken: 'panel' });
    expect(shared.image_url).toContain('share_token=panel');
    expect(projectTicket).not.toHaveBeenCalled();
  });
  it('clears private ticket caches when the account changes', async () => {
    const { access, logout } = setup();
    await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' });
    logout();
    expect(access.resolve('/api/v1/files/projects/p/renders/a.png')).not.toContain('asset_ticket');
  });
  it('requests the decoded exact storage key for filenames with spaces', async () => {
    const { access, fileTicket } = setup();
    const data = await access.prepare({ model_url: '/api/v1/files/library/a/My%20house.glb' });
    expect(fileTicket).toHaveBeenCalledWith('library/a/My house.glb');
    expect(data.model_url).toContain('My%20house.glb?file_ticket=one-file');
  });
  it('renews existing gallery URLs after a long session and notifies their consumers', async () => {
    vi.useFakeTimers();
    try {
      const { access, projectTicket } = setup();
      const image = (await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' })).image_url;
      const listener = vi.fn(); const unsubscribe = access.subscribe(listener);
      vi.advanceTimersByTime(16 * 60_000);
      expect(access.resolve(image)).not.toContain('asset_ticket');
      projectTicket.mockResolvedValueOnce({ asset_ticket: 'renewed-ticket', expires_in: 900 });
      await access.refresh();
      expect(access.resolve(image)).toContain('asset_ticket=renewed-ticket');
      expect(projectTicket).toHaveBeenCalledTimes(2); expect(listener).toHaveBeenCalledTimes(1);
      unsubscribe();
    } finally { vi.useRealTimers(); }
  });

  it('keeps renewal targets and object ownership after same-account token rotation and a sleeping tab', async () => {
    vi.useFakeTimers();
    try {
      const { access, projectTicket, fileTicket, setToken } = setup();
      const data = await access.prepare({ id: 'building-a', project_id: 'project-a',
        model_url: '/api/v1/buildings/building-a/model/file',
        video_url: '/api/v1/files/projects/project-a/videos/video.mp4',
        private_image: '/api/v1/files/render-audit/a/output.png',
      });
      const listener = vi.fn(); access.subscribe(listener);
      setToken(token('account-a', 2));
      // No resolve/prepare occurs before this focus/visibility renewal. The
      // existing gallery still holds its old decorated URLs after sleeping.
      vi.advanceTimersByTime(16 * 60_000);
      projectTicket.mockResolvedValueOnce({ asset_ticket: 'renewed-project', expires_in: 900 });
      fileTicket.mockResolvedValueOnce({ file_ticket: 'renewed-file', expires_in: 900 });
      await access.refresh();
      expect(projectTicket).toHaveBeenCalledTimes(2);
      expect(fileTicket).toHaveBeenCalledTimes(2);
      expect(access.resolve(data.video_url)).toContain('asset_ticket=renewed-project');
      expect(access.resolve(data.model_url)).toContain('asset_ticket=renewed-project');
      expect(access.resolve(data.private_image)).toContain('file_ticket=renewed-file');
      expect(listener).toHaveBeenCalledTimes(2);
    } finally { vi.useRealTimers(); }
  });

  it('does not discard a same-account ticket response when auth refresh rotates the login token in flight', async () => {
    const { access, projectTicket, setToken } = setup();
    const response = deferred<{ asset_ticket: string; expires_in: number }>();
    projectTicket.mockReturnValueOnce(response.promise);
    const pending = access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' });
    setToken(token('account-a', 2));
    response.resolve({ asset_ticket: 'same-account-result', expires_in: 900 });
    expect((await pending).image_url).toContain('asset_ticket=same-account-result');
  });

  it('drops credentials and renewal targets on logout, including immediate login to the same account', async () => {
    const { access, projectTicket, setToken, logout } = setup();
    const previous = await access.prepare({ id: 'building-a', project_id: 'p', model_url: '/api/v1/buildings/building-a/model/file' });
    const listener = vi.fn(); access.subscribe(listener);
    logout();
    expect(listener).toHaveBeenCalledOnce();
    setToken(token('account-a', 3));
    await access.refresh();
    expect(projectTicket).toHaveBeenCalledTimes(1);
    expect(access.resolve(previous.model_url)).not.toContain('asset_ticket');
  });

  it('clears old targets when a different account becomes active while the tab is hidden', async () => {
    const { access, projectTicket, setToken } = setup();
    const old = await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' });
    setToken(token('account-b'));
    await access.refresh();
    expect(projectTicket).toHaveBeenCalledTimes(1);
    expect(access.resolve(old.image_url)).not.toContain('asset_ticket');
    // Unknown object URLs must not retain a private ticket from old query data.
    expect(access.resolve('/api/v1/buildings/unknown/model/file?asset_ticket=account-a-ticket')).not.toContain('asset_ticket');
  });

  it('ignores old-account completion without deleting the new account pending request for the same key', async () => {
    const { access, projectTicket, setToken } = setup();
    const a = deferred<{ asset_ticket: string; expires_in: number }>();
    const b = deferred<{ asset_ticket: string; expires_in: number }>();
    projectTicket.mockReturnValueOnce(a.promise).mockReturnValueOnce(b.promise);
    const path = '/api/v1/files/projects/shared/renders/a.png';
    const first = access.prepare({ image_url: path });
    setToken(token('account-b'));
    const second = access.prepare({ image_url: path });
    a.resolve({ asset_ticket: 'old-account-ticket', expires_in: 900 });
    expect((await first).image_url).not.toContain('old-account-ticket');
    const third = access.prepare({ image_url: path });
    expect(projectTicket).toHaveBeenCalledTimes(2);
    b.resolve({ asset_ticket: 'new-account-ticket', expires_in: 900 });
    expect((await second).image_url).toContain('asset_ticket=new-account-ticket');
    expect((await third).image_url).toContain('asset_ticket=new-account-ticket');
  });

  it('an old-account renewal failure cannot remove the new account completed ticket', async () => {
    vi.useFakeTimers();
    try {
      const { access, projectTicket, setToken } = setup();
      const path = '/api/v1/files/projects/shared/renders/a.png';
      await access.prepare({ image_url: path });
      const oldRenewal = deferred<{ asset_ticket: string; expires_in: number }>();
      projectTicket.mockReturnValueOnce(oldRenewal.promise);
      vi.advanceTimersByTime(16 * 60_000);
      const oldRefresh = access.refresh();
      setToken(token('account-b'));
      projectTicket.mockResolvedValueOnce({ asset_ticket: 'new-account-ticket', expires_in: 900 });
      await access.prepare({ image_url: path });
      oldRenewal.reject(new Error('Old request failed'));
      await oldRefresh;
      expect(access.resolve(path)).toContain('asset_ticket=new-account-ticket');
    } finally { vi.useRealTimers(); }
  });

  it('treats the decoded access subject only as a cache identity and rejects other token forms', () => {
    expect(assetAccountIdentity(token('account-a', 1))).toBe(assetAccountIdentity(token('account-a', 2)));
    expect(assetAccountIdentity(token('account-a'))).not.toBe(assetAccountIdentity(token('account-b')));
    for (const value of [null, '', 'not-a-jwt', 'a.%%%.b', token('', 1), token('account-a', 1, 'refresh'), token('account-a', 1, 'file_asset')]) {
      expect(assetAccountIdentity(value)).toBeNull();
    }
  });
});
